import logging
logging.basicConfig(format='%(asctime)s.%(msecs)05d | %(levelname)s | %(filename)s:%(lineno)d | %(message)s' , datefmt='%FY%T')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
import requests

demo_user_details = {
  "user_id": "3f89e3f8-1870-4d9a-80db-adf9b8698ea6",
  "user_name": "Emma",
  "created_on": "2023-12-03T20:01:36.435544",
  "password": "Demo"
}

demo_user_device1 = {
  "device_id": "70340ad3-644f-4846-8b85-70ac627fd216",
  "device_name": "iPhone - Work",
  "owner_id": "3f89e3f8-1870-4d9a-80db-adf9b8698ea6",
  "created_on": "2023-12-03T20:03:17.019470",
  "status": "ACTIVE"
}

demo_user_device2 = {
  "device_id": "1c5a3057-1692-4818-bf1d-147ba660aa53",
  "device_name": "Android - Home",
  "owner_id": "3f89e3f8-1870-4d9a-80db-adf9b8698ea6",
  "created_on": "2023-12-03T20:03:50.797366",
  "status": "ACTIVE"
}



SERVICE_BASE_URL="http://10.0.0.5"


class LoginRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    user_name: str
    created_on: datetime = Field(default_factory=lambda: datetime.now().isoformat())

class TokenHeader(BaseModel):
    access_token: str
    token_type: str

def get_token_as_header(self):
        return {"Authorization": self.token_type + " " + self.access_token}

def login(username: str, password: str):

    request_content = LoginRequest(username=username, password=password).model_dump()
    login_service_url = SERVICE_BASE_URL+":4430/login"

    login_response = requests.post(login_service_url, data=request_content)
    if login_response.status_code==200:
        logger.info("Logged In")
        return TokenHeader(**login_response.json())
    raise PermissionError(login_response.json()['detail'])

if __name__ == "__main__":
    try:
        token = login("Emma", "Demo")
    except Exception as err:
        logger.error(str(err))
