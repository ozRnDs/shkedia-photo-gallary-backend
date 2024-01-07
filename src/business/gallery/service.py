import traceback
import os

from pydantic import BaseModel
from typing import List, Any
from cachetools import cached, TTLCache
from datetime import datetime, timedelta
import time

import pickle
from math import ceil
import logging
logger = logging.getLogger(__name__)

from project_shkedia_models.collection import CollectionPreview

from business.image_processing.service import ImageProcessingService
from business.db.media_service import MediaDBService, MediaDB, SearchResult, MediaObjectEnum, MediaThumbnail, Insight, InsightJob
from business.encryption.service import DecryptService
from business.db.user_service import UserDBService, User, Device

from .models import Page, MediaView

# Caching mechanism

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
        self.caching_retention = caching_retention_time_minutes


    def get_collections_for_user(self, token, engine_type, page_number=0, page_size=16):
        # self.__refresh_cache__(token=token, user_id=user_id, engine_type)
        collections_results = self.media_db_service.search_collections(token=token,engine_name=engine_type,page_number=page_number, page_size=page_size)
        if len(collections_results.results)==0:
            return SearchResult(total_results_number=0,results=[])
        collections_results.results = [CollectionPreview(**collection_item) for collection_item in collections_results.results]
        # for collection in collections_results.results:
        #     try:
        #         collection_thumbnail = self.decrypt_service.decrypt(collection.media_key, {"thumbnail": collection.thumbnail})
        #         collection_thumbnail = ImageProcessingService.get_image_base64(collection_thumbnail["thumbnail"])
        #         collection.thumbnail = collection_thumbnail
        #     except Exception as err:
        #         logger.warning(f"Failed to get the {collection.name} collection's thumbnail")
        return collections_results

    def get_collection_for_user(self,token,collection_name, engine_type, page_number=0, page_size=16):
        collection_details = self.media_db_service.get_collection_for_user(token=token,collection_name=collection_name, engine_name=engine_type)
        media_list = self.media_db_service.get_collection_media(token=token, collection_name=collection_name, engine_type=engine_type, page_number=page_number, page_size=page_size)
        collection_size = len(collection_details.media_list)
        media_list = Page(page_number=0,items=media_list,number_of_pages=ceil(collection_size/page_size))
        return collection_details, media_list
        
    # @cached(cache=TTLCache(maxsize=10, ttl=timedelta(hours=1), timer=datetime.now))
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

    @cached(cache=TTLCache(maxsize=100, ttl=timedelta(days=7), timer=datetime.now))
    def __decrypt_single_media(self, media: MediaThumbnail) -> MediaView:
        try:
            image = self.decrypt_service.decrypt(media.media_key,{"image": media.media_thumbnail})
            image = ImageProcessingService.get_image_base64(image["image"])
        except Exception as err:
            logger.warning(f"Failed to decrypt image {media.media_id}")
            image=""
        return MediaView(thumbnail=image,**media.model_dump())

    @cached(cache=TTLCache(maxsize=100, ttl=timedelta(days=7), timer=datetime.now))
    def get_media(self, token, media_id: str) -> bytes:
        media_object = self.media_db_service.get_media_by_id(token,media_id,response_type=MediaObjectEnum.MediaThumbnail)
        media_object = MediaThumbnail(**media_object)

        image = self.decrypt_service.decrypt(media_object.media_key,{"image": media_object.media_thumbnail})["image"]

        return image

