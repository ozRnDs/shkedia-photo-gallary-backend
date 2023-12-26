import requests
import pickle
import os
import time
from pydantic import BaseModel
from typing import List

base_url = "https://picsum.photos/"
SAVE_BASE_LOCATION = os.getcwd()+"/dev/data"
DB_FILE_NAME = f"{SAVE_BASE_LOCATION}/images.pickle"

class RandomImage(BaseModel):
    id: str
    author: str
    width: int
    height: int
    url: str
    download_url: str

def get_list_of_images(number_of_images) -> List[RandomImage]:
    
    params = {
        "limit": number_of_images,
        "page": 6
    }

    images_list_url = f"{base_url}/v2/list"
    response = requests.get(images_list_url, params=params)

    modeled_list = []
    for image in response.json():
        modeled_list.append(RandomImage(**image))

    return modeled_list

def save_object(file_name, object_to_save):
    with open(file_name,"wb") as file:
        pickle.dump(object_to_save, file, protocol=pickle.HIGHEST_PROTOCOL)

def load_list_of_images_from_file(file_name) -> List[RandomImage]:
    with open(file_name, "rb") as file:
        list_of_images = pickle.load(file)

    return list_of_images

def download_and_save_image(image_url, image_name):

    try:
        response = requests.get(image_url)

        with open(image_name, "wb") as f:
            f.write(response.content)
    except Exception as err:
        print(str(err))


if __name__ == '__main__':

    list_of_images = get_list_of_images(100)
    save_object(DB_FILE_NAME, list_of_images)

    # list_of_images = load_list_of_images_from_file(DB_FILE_NAME)

    for image in list_of_images:
        image_path = f"{SAVE_BASE_LOCATION}/{image.id}.jpg"
        if os.path.exists(image_path):
            continue
        print(f"Downloading image number {image.id}")
        download_and_save_image(image.download_url, image_path)
        time.sleep(0.2)

    print(f"finished Downloading the Images")