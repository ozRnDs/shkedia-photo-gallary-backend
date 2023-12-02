import logging
logger = logging.getLogger(__name__)
from typing import List
import requests
import json
from pydantic import BaseModel

from business.authentication.models import Token
from business.models.medias import MediaRequest, MediaDB, SearchResult

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

    def search_media(self, token: Token, **kargs) -> SearchResult:
        insert_url = self.service_url+"/v1/media/search"
        search_response = requests.get(insert_url,params=kargs, headers=token.get_token_as_header())

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


        
