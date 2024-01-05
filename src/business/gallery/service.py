import traceback
import os
from pydantic import BaseModel
from typing import List, Any
from datetime import datetime, timedelta
import time
import pickle
from math import ceil
import logging
logger = logging.getLogger(__name__)

from project_shkedia_models.collection import CollectionPreview

from business.image_processing.service import ImageProcessingService
from business.db.media_service import MediaDBService, MediaDB, SearchResult, MediaObjectEnum, MediaThumbnail, Insight, InsightJob
from project_shkedia_models.jobs import InsightJobStatus
from business.encryption.service import DecryptService
from business.db.user_service import UserDBService, User, Device
from business import utils

# Caching mechanism
class Album(BaseModel):
    name: str
    date: datetime
    images_list: List[MediaThumbnail]
    b64_preview_image: str

    @property
    def canvas_thumbnail(self):
        return self.b64_preview_image
    
    @property
    def canvas_right_description(self):
        return f"{len(self.images_list)} Images"
    
    @property
    def canvas_left_description(self):
        return f"{self.name}"
    
    @property
    def canvas_url_base(self):
        return f"album_view"

    @property
    def canvas_url_id(self):
        return self.name

class Page(BaseModel):
    page_number: int
    items: Any
    number_of_pages: int

class MediaView(MediaThumbnail):
    thumbnail: str
    user: User | None = None
    device: Device | None = None

    @property
    def canvas_thumbnail(self):
        return self.thumbnail
    
    @property
    def canvas_right_description(self):
        return utils.sizeof_fmt(self.media_size_bytes)
    
    @property
    def canvas_left_description(self):
        return self.created_on.strftime("%d/%m %H:%M")
    
    @property
    def canvas_url_base(self):
        return f"media_view"
    
    @property
    def canvas_url_id(self):
        return self.media_id

class CacheMemory(BaseModel):
    albums_list: List[Album] = []
    list_of_images: List[MediaDB] = []
    is_working: bool = False
    last_updated: datetime = datetime(year=1970, month=1, day=1)
    retention_time_minutes: int = 300

    def is_updated(self):
        if self.last_updated + timedelta(minutes=self.retention_time_minutes) < datetime.now():
            return False
        return True

    def unlock(self):
        if self.is_working:
            self.last_updated = datetime.now()
        self.is_working=False

    def lock(self):
        self.is_working=True

class MediaGalleryService():

    def __init__(self,
                 media_db_service: MediaDBService,
                 user_db_service: UserDBService,
                 decrypt_service: DecryptService,
                 local_cache_location: str = "/temp/local_cache.pickle",
                 caching_retention_time_minutes: int = 120,
                 items_in_page: int = 16,
                 debug_mode: bool = True
                 ):
        self.items_in_page = items_in_page
        self.media_db_service = media_db_service
        self.user_db_service = user_db_service
        self.decrypt_service = decrypt_service
        self.debug_mode = debug_mode
        self.local_cache_location = local_cache_location
        self.cache_object = self.__load_cache_locally__()
        self.caching_retention = caching_retention_time_minutes


    def __load_cache_locally__(self):
        local_cache_file_location = self.local_cache_location
        try:
            if os.path.exists(local_cache_file_location):
                with open(local_cache_file_location,"rb") as file:
                    logger.info("Loading Media from cache")
                    cache_object = pickle.load(file)
                    for user in cache_object:
                        cache_object[user].unlock()
                    return cache_object
        except Exception as err:
            traceback.print_exc()
            logger.warning(f"Could not load local cache: {str(err)}")
        return {}

    def __save_cache_locally__(self):
        logger.info("Backing up cache object")
        local_cache_file_location=self.local_cache_location
        with open(local_cache_file_location, "wb") as file:
            pickle.dump(self.cache_object,file, protocol=pickle.HIGHEST_PROTOCOL)
            

    def get_collections_for_user(self, token, engine_type, page_number=0, page_size=16):
        # self.__refresh_cache__(token=token, user_id=user_id, engine_type)
        collections_results = self.media_db_service.search_collections(token=token,engine_name=engine_type,page_number=page_number, page_size=page_size)
        if len(collections_results.results)==0:
            return SearchResult(total_results_number=0,results=[])
        collections_results.results = [CollectionPreview(**collection_item) for collection_item in collections_results.results]
        for collection in collections_results.results:
            collection_thumbnail = self.decrypt_service.decrypt(collection.media_key, {"thumbnail": collection.thumbnail})
            collection_thumbnail = ImageProcessingService.get_image_base64(collection_thumbnail["thumbnail"])
            collection.thumbnail = collection_thumbnail
        return collections_results

    def get_collection_for_user(self,token,collection_name, engine_type, page_number=0, page_size=16):
        collection_details = self.media_db_service.get_collection_for_user(token=token,collection_name=collection_name, engine_name=engine_type)
        media_list = self.media_db_service.get_collection_media(token=token, collection_name=collection_name, engine_type=engine_type, page_number=page_number, page_size=page_size)
        collection_size = len(collection_details.media_list)
        media_list = Page(page_number=0,items=media_list,number_of_pages=ceil(collection_size/page_size))
        return collection_details, media_list
        

    def get_page_content(self, items_list, page_number)-> Page:
        if len(items_list) == 0:
            return Page(page_number=0,items=[],number_of_pages=0)
        number_of_pages = ceil(len(items_list)/self.items_in_page)
        start_index = (page_number-1)*self.items_in_page
        end_index = start_index + self.items_in_page
        end_index = len(items_list) if len(items_list) < end_index else end_index
        if "date" in items_list[0].model_dump():
            items_list.sort(key=lambda x:x.date, reverse=True)
        if "created_on" in items_list[0].model_dump():
            items_list.sort(key=lambda x:x.created_on, reverse=True)
        return Page(page_number=page_number,
                    number_of_pages=number_of_pages,
                    items=items_list[start_index:end_index])

    def decrypt_list_of_medias(self, medias_list: List[MediaThumbnail])-> List[MediaView]:
        decrypted_list = []
        for media in medias_list:
            decrypted_list.append(self.__decrypt_single_media(media))
        return decrypted_list

    def __decrypt_single_media(self, media: MediaThumbnail) -> MediaView:
        image = self.decrypt_service.decrypt(media.media_key,{"image": media.media_thumbnail})
        image = ImageProcessingService.get_image_base64(image["image"])
        return MediaView(thumbnail=image,**media.model_dump())


    def get_media_content(self, token, media_id, user_id) -> MediaView:
        # media_content = [media for media in self.cache_object[user_id].list_of_images if media.media_id==media_id][-1]
        # if media_content is None:
        #     raise Exception("Could find media")
        media = self.media_db_service.search_media(token=token,media_id=media_id,response_type=MediaObjectEnum.MediaThumbnail)
        media = self.__decrypt_single_media(MediaThumbnail(**media.results[0]))
        media.user = self.user_db_service.search_user(token, search_field="user_id", search_value=media.owner_id)
        media.device = self.user_db_service.get_device(token, device_id=media.device_id)
        return media
    
    def get_media_insights(self, token, media_id):
        insights_list = self.media_db_service.search_insights(token,media_id=media_id)
        jobs_list = self.media_db_service.search_jobs(token, media_id=media_id)
        jobs_list = [job_item for job_item in jobs_list if job_item.status != InsightJobStatus.DONE]

        return insights_list,jobs_list