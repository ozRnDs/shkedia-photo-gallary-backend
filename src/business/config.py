import os
import logging
logging.basicConfig(format='%(asctime)s.%(msecs)05d | %(levelname)s | %(filename)s:%(lineno)d | %(message)s' , datefmt='%FY%T')

class ApplicationConfiguration:

    RECONNECT_WAIT_TIME: int = 1
    RETRY_NUMBER: int = 10

    # Authentication Configuration values
    JWT_KEY_LOCATION: str = "/temp/jwt_token"
    AUTH_SERVICE_URL: str = "CHANGE ME"
    TOKEN_TIME_PERIOD: int = 15

    # DB Configuration values
    MEDIA_DB_HOST: str = "10.0.0.5"
    MEDIA_DB_PORT: str = "4431"
    MEDIA_REPO_HOST: str = "10.0.0.5"
    MEDIA_REPO_PORT: str = "4432"
    USER_DB_HOST: str = "10.0.0.5"
    USER_DB_PORT: str = "4430"

    # Image Processing Parameters
    THUMBNAIL_MAX_WIDTH: int = 500
    THUMBNAIL_MAX_HEIGHT: int = 500

    # Encryption Configuration Values
    PUBLIC_KEY_LOCATION: str = ".local/data.pub"
    PRIVATE_KEY_LOCATION: str = ".local/data"

    LOCAL_CACHE_LOCATION: str = "/temp/local_cache.pickle"
    
    def __init__(self) -> None:
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.info("Start App")

        self.extract_env_variables()
        

    def extract_env_variables(self):
        for attr, attr_type in self.__annotations__.items():
            try:
                self.__setattr__(attr, (attr_type)(os.environ[attr]))
            except Exception as err:
                self.logger.warning(f"Couldn't find {attr} in environment. Run with default value")
        
app_config = ApplicationConfiguration()