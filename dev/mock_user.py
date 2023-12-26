import logging
logging.basicConfig(format='%(asctime)s.%(msecs)05d | %(levelname)s | %(filename)s:%(lineno)d | %(message)s' , datefmt='%FY%T')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from datetime import datetime

import sys,os
sys.path.append(f"{os.getcwd()}/dev")
sys.path.append(f"{os.getcwd()}/src")


from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import uuid4
from PIL import Image
import pickle

from datetime import datetime, timedelta
from random import randrange

import requests

from harvest_images import RandomImage, load_list_of_images_from_file, DB_FILE_NAME
from business.models.medias import MediaRequest, MediaDB

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

class ImageRequest(BaseModel):
    name: str
    date: int
    dateStr: str
    uri: str
    size: int
    camera_model: str
    camera_maker: str

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

class SearchResult(BaseModel):
    total_results_number: int
    page_number: int = 0
    page_size: int | None = None
    results: List[MediaDB]

def login(username: str, password: str)->TokenHeader:

    request_content = LoginRequest(username=username, password=password).model_dump()
    login_service_url = SERVICE_BASE_URL+":4430/login"

    login_response = requests.post(login_service_url, data=request_content)
    if login_response.status_code==200:
        logger.info("Logged In")
        return TokenHeader(**login_response.json())
    raise PermissionError(login_response.json()['detail'])

def generate_images_data(images_list: List[RandomImage], devices_list: List[str]) -> Dict[str,List[MediaRequest]]:
    
    start_date = datetime(year=2022,month=4,day=1)
    
    
    images_metadata = {}
    for image_data in images_list:
        random_date = randrange(864000)
        target_device = devices_list[random_date % 2]
        if not target_device in images_metadata:
            images_metadata[target_device]=[]
        
        image_device_path = BASE_IMAGES_LOCATION+f"/{image_data.id}.jpg"
        image = Image.open(image_device_path)
        
        temp_image_metadata = ImageRequest(name=f"Image {image_data.id}",
                                            size=os.stat(image_device_path).st_size,
                                            dateStr=(start_date+timedelta(minutes=random_date)).isoformat(),
                                            date=(start_date+timedelta(minutes=random_date)).timestamp(),
                                            uri=image_data.download_url, camera_maker="", camera_model=""
                                            ) # type: ignore
        images_metadata[target_device].append(temp_image_metadata)
    return images_metadata

def upload_meta_data(token, images_list: List[MediaRequest], device_id, user_name):
    upload_images_list_service_url = f"{SERVICE_BASE_URL}:4433/images/list"

    json_list = []
    for media in images_list:
        json_list.append(media.model_dump())

    params = { 
        "user_name": user_name,
        "device_id": device_id
    }

    response = requests.post(upload_images_list_service_url,json=json_list,params=params,headers=token.get_token_as_header())


    if response.status_code == 200:
        return response.json()

def save_object(file_name, object_to_save):
    with open(file_name,"wb") as file:
        pickle.dump(object_to_save, file, protocol=pickle.HIGHEST_PROTOCOL)

def load_object(file_name):
    with open(file_name, "rb") as file:
        object = pickle.load(file_name)

    return object


def search_media(token: TokenHeader, **kargs) -> SearchResult:
    insert_url = "http://10.0.0.5:4431/v1/media/search"
    search_response = requests.get(insert_url,params=kargs, headers=token.get_token_as_header())

    if search_response.status_code == 200:
        return SearchResult(**search_response.json())
    if search_response.status_code == 404:
        return SearchResult(total_results_number=0, results=[])
    raise Exception(search_response.json()["detail"])


def put_image_file(token: TokenHeader, image_local_path, device_id: str, user_name: str, image_name:str, image_id: str, uri: str, overwrite=False):
    #SETUP
    with open(image_local_path,'rb') as image_file:
        image_bytes = image_file.read()
    
    files={"image": image_bytes}

    data = { "device_id": device_id ,
              "user_name": user_name,
               "image_name": image_name,
                "image_id":  image_id,
                "uri": uri,
                "overwrite": overwrite}

    # RUN
    results = requests.put("http://10.0.0.5:4433/images",data=data, files=files ,headers=token.get_token_as_header())

    # ASSERT
    if results.status_code == 200:
        return
    raise Exception(f"Failed to upload: {str(results)}")


if __name__ == "__main__":
    BASE_IMAGES_LOCATION = f"{os.getcwd()}/dev/data"
    devices_list = ["70340ad3-644f-4846-8b85-70ac627fd216", "1c5a3057-1692-4818-bf1d-147ba660aa53"]
    try:
        #TODO: Create information list of the images
        images_list: List[RandomImage] = load_list_of_images_from_file(DB_FILE_NAME)
        
        # generated_meta_data = generate_images_data(images_list, devices_list=devices_list)

        token = login("Emma", "Demo")
        #Upload the data to the db

        # counter = 3
        # for device_id in generated_meta_data:
        #     media_metadata_upload_response = upload_meta_data(token=token,images_list=generated_meta_data[device_id],device_id=device_id, user_name=demo_user_details["user_name"])
        #     save_object(f"{os.getcwd()}/dev/data/image_metadata-device-{counter}.pickle", media_metadata_upload_response)        
        
        #TODO: Upload the images to the service
        uploaded_image = [
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/3.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/7.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/8.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/9.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/11.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/13.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/16.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/19.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/20.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/24.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/27.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/29.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/30.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/35.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/40.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/41.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/42.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/45.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/46.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/47.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/48.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/50.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/51.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/58.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/60.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/62.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/63.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/64.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/67.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/68.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/72.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/74.jpg",
                                "/workspaces/shkedia-photo-gallery-backend/dev/data/75.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/76.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/77.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/78.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/79.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/80.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/81.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/82.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/83.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/84.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/85.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/87.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/88.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/89.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/90.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/91.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/92.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/93.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/94.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/95.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/96.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/98.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/99.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/100.jpg",
"/workspaces/shkedia-photo-gallery-backend/dev/data/101.jpg",

                                        ]
        for device_id in devices_list:
            search_result = search_media(token=token, device_id=device_id)
            logger.info(f"Uploading medias for device: {devices_list[0]}")
            for result in search_result.results:
                image_path = os.getcwd() + "/dev/data/" + result.media_name.replace("Image ","")+".jpg"
                if image_path in uploaded_image or result.upload_status=="UPLOADED":
                    continue
                put_image_file(token=token,image_local_path=image_path, device_id=result.device_id, user_name="Emma", image_name=result.media_name,
                               image_id=result.media_id, uri=result.device_media_uri)
                uploaded_image.append(image_path)
                logger.info(f"Uploaded image {image_path}")
        save_object(f"{os.getcwd()}/dev/data/uploaded_images_list.pickle", uploaded_image)
    except Exception as err:
        logger.error(str(err))
