
from jose import JWTError, jwt
from typing import Annotated
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import timedelta, datetime

from db.media_service import MediaDBService
from models.user import UserDB


class TokenData(BaseModel):
    username: str | None = None

class AuthService:
    def __init__(self,
                 db_service: MediaDBService=None,
                 jwt_key_location: str=None,                
                 default_expire_delta_min: int=15,
                 jwt_algorithm: str="HS256") -> None:
        self.db_service = db_service
        self.jwt_key_location = jwt_key_location
        self.jwt_algorithm = jwt_algorithm
        # self.session_token: str = self.__create_session_token__(service_token_location)
        # self.user_service_uri = user_service_uri
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.default_expire_delta = timedelta(minutes=default_expire_delta_min)
        self.router = self.__initialize_routes__()


    def __initialize_routes__(self):
        router = APIRouter(tags=["Login"])
        router.add_api_route(path="", 
                             endpoint=self.__log_in__,
                             methods=["post"]
                             )
        return router

    def __log_in__(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        user = self.db_service.select(UserDB, user_name=form_data.username)
        if user is None:
            raise credentials_exception
        if not self.verify_password(form_data.password, user.password):
            raise credentials_exception
        access_token = self.create_access_token(data={"sub": user.user_name})
        return {"access_token": access_token, "token_type": "bearer"}

    def __get_jwt_key__(self):
        with open(self.jwt_key_location, 'r') as file:
            temp_token = file.read()
        return temp_token

    
    def auth_request(self, request):
        #TODO: Get user's token and check that is valid with the system's auth service
        return True
        pass

    def __get_user_from_token__(self, token: Annotated[str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        return
        try:
            payload = jwt.decode(token, self.__get_jwt_key__(), algorithms=[self.jwt_algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = self.db_service.select(UserDB, user_name=username)
        if user is None:
            raise credentials_exception
        return user
    
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: timedelta | None=None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta if expires_delta else self.default_expire_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.__get_jwt_key__() ,algorithm=self.jwt_algorithm)
        return encoded_jwt