import logging
logger = logging.getLogger(__name__)
from typing import List
import requests
import json
from pydantic import BaseModel

from business.authentication.models import Token
from project_shkedia_models.user import UserDB, UserRequest, User
from project_shkedia_models.device import Device, DeviceRequest


def retry(max_retries=5):
    def __external_wrapper__(fun):
        def __internal_wrapper__(*args, **kargs):
            retry_counter = 0
            error = None
            while retry_counter<max_retries:
                try:
                    return fun(*args, **kargs)
                except PermissionError as err:
                    raise err
                except Exception as err:
                    error = err
                    retry_counter+=1
            logger.error(f"Error repeated: {max_retries} times: {str(error)}")
            raise error

        return __internal_wrapper__
    return __external_wrapper__


class UserDBService:

    def __init__(self,
                 host: str,
                 port: str | int,
                 connection_timeout: int=10,
                 max_retries: int = 5
                 ) -> None:
        self.service_url = f"http://{host}:{str(port)}"
        self.connection_timeout = connection_timeout
        self.max_retries = max_retries

    def is_ready(self):
        raise NotImplementedError("Is it necessary?")

    def insert_user(self, user: UserRequest) -> User:
        
        insert_url = self.service_url+"/user"

        content = {
            "username": user.user_name,
            "password": user.password
        }

        insert_response = requests.put(insert_url, json=content)

        if insert_response.status_code == 200:
            return User(**insert_response)
        raise Exception(insert_response.json()["detail"])

    @retry(max_retries=5) # TODO: Think how to set it from the config
    def login_user(self, user: UserRequest) -> Token:
        
        login_url = self.service_url+"/login"
        data = {
            "username":user.user_name,
            "password":user.password
        }
        login_response = requests.post(login_url, data=data)

        if login_response.status_code == 200:
            return Token(**login_response.json())
        if login_response.status_code == 401:
            raise PermissionError("Permission Denied")
        raise Exception(login_response.json()["detail"])

    def search_user(self, token: Token, search_value: str, search_field: str="user_name") -> User:
        
        search_user_url = self.service_url+"/user"

        params = { "search_field": search_field,
                  "search_value": search_value
                  }

        search_user_response = requests.get(search_user_url, params=params, headers=token.get_token_as_header())

        if search_user_response.status_code == 200:
            return User(**search_user_response.json())
        raise Exception(search_user_response.json()["detail"])

    def search_device(self, token: Token, **kargs) -> List[Device]:
        
        search_device_url = self.service_url+"/device/search"

        search_device_response = requests.get(search_device_url, params=kargs, headers=token.get_token_as_header())

        if search_device_response.status_code == 200:
            devices = search_device_response.json()
            if not type(devices) is list:
                devices = [devices]
            devices = [Device(**device) for device in devices]
            return devices
        if search_device_response.status_code == 404:
            return []
        raise Exception(search_device_response.json()["detail"])
    
    def get_device(self, token: Token, device_id) -> Device | None:
        
        get_device_url = self.service_url+f"/device/{device_id}"

        get_device_response = requests.get(get_device_url, headers=token.get_token_as_header())

        if get_device_response.status_code == 200:
            return Device(**get_device_response.json())
        if get_device_response.status_code == 400:
            return None
        raise Exception(get_device_response.json()["detail"])

    def insert_device(self, token: Token, device_request: DeviceRequest) -> Device:
        
        insert_device_url = self.service_url+"/device"

        insert_device_response = requests.put(insert_device_url, json=device_request.model_dump(), headers=token.get_token_as_header())

        if insert_device_response.status_code == 200:
            return Device(**insert_device_response.json())
        raise Exception(insert_device_response.json()["detail"])