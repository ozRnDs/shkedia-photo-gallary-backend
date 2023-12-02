import io
from PIL import Image, ExifTags
import base64
import logging
logger = logging.getLogger(__name__)

class ImageProcessingService:

    def __init__(self, 
                 thumbnail_width_size: int=400,
                 thumbnail_height_size: int=200):
        self.thumbnail_width_size = thumbnail_width_size
        self.thumbnail_height_size = thumbnail_height_size

    def get_image_thumbnail_bytes(self, image_file) -> bytes:
        try:
            temp_image = Image.open(image_file)
            temp_image = ImageProcessingService.rotate_image(temp_image)
            exif = temp_image.info['exif']

            w,h = temp_image.size
            image_aspect_ratio = h/w
            image_format = temp_image.format
            temp_image = temp_image.resize((self.thumbnail_width_size, int(self.thumbnail_width_size*image_aspect_ratio)))

            mem_file = io.BytesIO()
            temp_image.save(mem_file, format=image_format, exif=exif)
            image_byte_array = mem_file.getvalue()
            mem_file.close()
            # target_file = io.StringIO()
            # temp_image.save(target_file)
            # temp_image.close()
            return image_byte_array
        except Exception as err:
            raise Exception(f"Failed to create thumbnail to image: {str(err)}")

    @staticmethod
    def get_image_base64(image: bytes) -> str:
        return base64.b64encode(image).decode() 
    
    @staticmethod
    def rotate_image(image: Image) -> str:
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=="Orientation":
                    break

            exif = image._getexif()

            if exif[orientation] == 3:
                image=image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image=image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image=image.rotate(90, expand=True)

            return image
        
        except (AttributeError, KeyError, IndexError):
            logger.info("Image doesn't have tags :(")
            return image
            pass
        
