import os
from pydantic import BaseModel
from typing import List, Any
from datetime import datetime, timedelta
import time
import pickle
from math import ceil
import logging
logger = logging.getLogger(__name__)

from business.image_processing.service import ImageProcessingService
from business.db.media_service import MediaDBService, MediaDB, SearchResult
from business.encryption.service import DecryptService
from business.db.user_service import UserDBService, User, Device

# Caching mechanism
class Album(BaseModel):
    name: str
    date: datetime
    images_list: List[MediaDB]
    b64_preview_image: str

class Page(BaseModel):
    page_number: int
    items: Any
    number_of_pages: int

class MediaView(MediaDB):
    thumbnail: str
    user: User | None = None
    device: Device | None = None

class CacheMemory(BaseModel):
    albums_list: List[Album] = []
    list_of_images: List[MediaDB] = []
    is_working: bool = False
    last_updated: datetime = datetime(year=1970, month=1, day=1)
    retention_time_minutes: int = 1000

    def is_updated(self):
        if self.last_updated + timedelta(minutes=self.retention_time_minutes) < datetime.now():
            return False
        return True

    def unlock(self):
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
        if os.path.exists(local_cache_file_location):
            with open(local_cache_file_location,"rb") as file:
                logger.info("Loading Media from cache")
                return pickle.load(file)
        return {}

    def __save_cache_locally__(self):
        logger.info("Backing up cache object")
        local_cache_file_location=self.local_cache_location
        with open(local_cache_file_location, "wb") as file:
            pickle.dump(self.cache_object,file, protocol=pickle.HIGHEST_PROTOCOL)
            

    def __refresh_cache__(self, token, user_id):
        if not user_id in self.cache_object:
            self.cache_object[user_id] = CacheMemory()
        if self.cache_object[user_id].is_working:
            while self.cache_object[user_id].is_working:
                time.sleep(1)
        try:
            if self.cache_object[user_id].is_updated():
                return
            self.cache_object[user_id].lock()
            logger.info(f"Loading Media from Media DB")
            search_results = self.media_db_service.search_media(token=token, owner_id=user_id, upload_status="UPLOADED")
            self.cache_object[user_id].list_of_images=search_results.results
            self.__group_medias_per_month__(search_results.results, user_id)
            self.__save_cache_locally__()
        except Exception as err:
            logger.error(f"Something went wrong: {str(err)}")
        finally:
            self.cache_object[user_id].unlock()

    def __group_medias_per_month__(self, media_list: List[MediaDB], user_id:str):
        temp_album_dict = {}

        for media in media_list:
            if media.upload_status!="UPLOADED":
                continue
            album_name = media.created_on.strftime("%m-%Y")
            if not album_name in temp_album_dict:
                temp_album_dict[album_name]=[]
            temp_album_dict[album_name].append(media)
        
        for album_name, images_list in temp_album_dict.items():
            cover_media: MediaDB = images_list[0]
            album_thumbnail = self.decrypt_service.decrypt(cover_media.media_key, {"thumbnail": cover_media.media_thumbnail})
            album_thumbnail = ImageProcessingService.get_image_base64(album_thumbnail["thumbnail"])
            self.cache_object[user_id].albums_list.append(Album(
                name=album_name, date=datetime(year=cover_media.created_on.year,
                                                month=cover_media.created_on.month,
                                                day=1),
                                                images_list=images_list,
                                                b64_preview_image=album_thumbnail
                                                ))

    def albums_list_for_user(self, token, user_id):
        if not user_id in self.cache_object:
            self.__refresh_cache__(token=token, user_id=user_id)
        return self.cache_object[user_id].albums_list

    def get_page_content(self, items_list, page_number)-> Page:
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

    def decrypt_list_of_medias(self, medias_list: List[MediaDB])-> List[MediaView]:
        decrypted_list = []
        for media in medias_list:
            decrypted_list.append(self.__decrypt_single_media(media))
        return decrypted_list

    def __decrypt_single_media(self, media: MediaDB) -> MediaView:
        image = self.decrypt_service.decrypt(media.media_key,{"image": media.media_thumbnail})
        image = ImageProcessingService.get_image_base64(image["image"])
        return MediaView(thumbnail=image,**media.model_dump())


    def get_media_content(self, token, media_id, user_id) -> MediaView:
        media_content = [media for media in self.cache_object[user_id].list_of_images if media.media_id==media_id][-1]
        if media_content is None:
            raise Exception("Could find media")
        media = self.__decrypt_single_media(media_content) 
        media.user = self.user_db_service.search_user(token, search_field="user_id", search_value=media.owner_id)
        media.device = self.user_db_service.search_device(token, device_id=media.device_id)
        return media
        