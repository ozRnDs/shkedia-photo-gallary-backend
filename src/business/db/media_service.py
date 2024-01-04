import logging
logger = logging.getLogger(__name__)
from typing import List
from requests.adapters import HTTPAdapter, Retry
import requests
import json
from pydantic import BaseModel

from business.authentication.models import Token
from project_shkedia_models.media import MediaRequest, MediaDB, MediaObjectEnum, MediaThumbnail
from project_shkedia_models.search import SearchResult
from project_shkedia_models.collection import CollectionPreview

class MediaDBService:

    def __init__(self,
                 host: str,
                 port: str | int,
                 connection_timeout: int=10
                 ) -> None:
        self.service_url = f"http://{host}:{str(port)}"
        self.connection_timeout = connection_timeout

       
    def is_ready(self):
        raise NotImplementedError("Is it necessary?")

    def insert_media(self, token: Token, media: MediaRequest) -> MediaDB:
        content = media.model_dump_json()

        insert_url = self.service_url+"/v1/media"
        insert_response = requests.put(insert_url,json=json.loads(content), headers=token.get_token_as_header())

        if insert_response.status_code == 200:
            return MediaDB(**insert_response.json())
        raise Exception(insert_response.json()["detail"])
    
    def get(self, token: Token, media_id) -> MediaDB:
        insert_url = self.service_url+"/v1/media/"+media_id
        insert_response = requests.get(insert_url, headers=token.get_token_as_header())

        if insert_response.status_code == 200:
            return MediaDB(**insert_response.json())
        raise Exception(insert_response.json()["details"])

    def get_collection_media(self, token:Token, collection_name, engine_type, **kargs) -> List[MediaThumbnail]:
        get_collection_by_name = self.service_url+f"/v2/insights-engines/{engine_type}/collections/{collection_name}/media"

        s = requests.Session()

        retries = Retry(total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504])

        s.mount('http://', HTTPAdapter(max_retries=retries))

        search_response = requests.get(get_collection_by_name,params=kargs, headers=token.get_token_as_header())

        s.close()

        if search_response.status_code == 200:
            search_response = SearchResult(**search_response.json())
            return [MediaThumbnail(**media_item) for media_item in search_response.results]
        if search_response.status_code == 404:
            raise FileNotFoundError()
        if search_response.status_code == 401:
            raise PermissionError(search_response.json()["detail"])
        raise Exception(search_response.json()["detail"])

    def get_collection_for_user(self, token:Token, collection_name, engine_name) -> CollectionPreview:
        get_collection_by_name = self.service_url+f"/v2/insights-engines/{engine_name}/collections/{collection_name}"

        s = requests.Session()

        params = {
            "engine_name": engine_name
        }

        retries = Retry(total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504])

        s.mount('http://', HTTPAdapter(max_retries=retries))

        search_response = requests.get(get_collection_by_name, params=params, headers=token.get_token_as_header())

        s.close()

        if search_response.status_code == 200:
            search_results = SearchResult(**search_response.json())
            if search_results.total_results_number == 0:
                raise FileNotFoundError()
            search_results = [CollectionPreview(**collection_item) for collection_item in search_results.results]
            for collection in search_results:
                if collection.engine_name == engine_name:
                    return collection

        if search_response.status_code == 404:
            raise FileNotFoundError(search_response.json()["detail"])
        if search_response.status_code == 401:
            raise PermissionError(search_response.json()["detail"])
        raise Exception(search_response.json()["detail"])

    def search_collections(self, token: Token, engine_name: str, **kargs) -> SearchResult:

        search_collection_url = self.service_url+f"/v2/insights-engines/{engine_name}/collections"

        s = requests.Session()

        retries = Retry(total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504])

        s.mount('http://', HTTPAdapter(max_retries=retries))

        search_response = requests.get(search_collection_url,params=kargs, headers=token.get_token_as_header())

        s.close()

        if search_response.status_code == 200:
            return SearchResult(**search_response.json())
        if search_response.status_code == 404:
            return SearchResult(total_results_number=0, results=[])
        if search_response.status_code == 401:
            raise PermissionError(search_response.json()["detail"])
        raise Exception(search_response.json()["detail"])

    def search_media(self, token: Token, **kargs) -> SearchResult:
        insert_url = self.service_url+"/v1/media/search"

        s = requests.Session()

        retries = Retry(total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504])

        s.mount('http://', HTTPAdapter(max_retries=retries))

        search_response = requests.get(insert_url,params=kargs, headers=token.get_token_as_header())

        s.close()

        if search_response.status_code == 200:
            return SearchResult(**search_response.json())
        if search_response.status_code == 404:
            return SearchResult(total_results_number=0, results=[])
        raise Exception(search_response.json()["detail"])
    
    def delete(self, token: Token, media_id) -> MediaDB:
        insert_url = self.service_url+"/v1/media/"+media_id
        insert_response = requests.delete(insert_url, headers=token.get_token_as_header())

        if insert_response.status_code == 200:
            return MediaDB(**insert_response.json())
        raise Exception(insert_response.json()["detail"])
    
    def update(self, token: Token, media: MediaDB):
        insert_url = self.service_url+"/v1/media/"+media.media_id
        content = media.model_dump_json()
        insert_response = requests.post(insert_url, json=json.loads(content), headers=token.get_token_as_header())

        if insert_response.status_code == 200:
            return MediaDB(**insert_response.json())
        raise Exception(insert_response.json()["detail"])


        
