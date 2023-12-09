
import json
from jose import JWTError, jwt
from typing import Annotated
from passlib.context import CryptContext

from django.http import HttpRequest, HttpResponseRedirect, HttpResponseForbidden
from pydantic import BaseModel
from datetime import timedelta, datetime


from business.db.user_service import UserDBService, UserRequest, User
from business.authentication.models import Token


class TokenData(BaseModel):
    sub: str | None = None
    auth_token: Token | None = None


class AuthService:
    def __init__(self,
                 db_user_service: UserDBService,          
                login_redirect_path: str="/login",
                 default_expire_delta_min: int=15,
                 jwt_key_location: str=None, 
                 jwt_algorithm: str="HS256") -> None:
        self.user_db_service = db_user_service
        self.login_redirect_path = login_redirect_path

        self.default_expire_delta = timedelta(minutes=default_expire_delta_min)
        self.jwt_key_location = jwt_key_location
        self.jwt_algorithm = jwt_algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.default_expire_delta = timedelta(minutes=default_expire_delta_min)
        #TODO: Add jwt key generation mechanism

    def log_in(self, username: str, password: str, redirect_to: str="/"):


        auth_token = self.user_db_service.login_user(user=UserRequest(username=username, password=password))
        user_data = self.user_db_service.search_user(auth_token,search_value=username)
        gallery_token_data = TokenData(sub=user_data.user_name, auth_token=auth_token)
        gallery_access_token = self.create_access_token(data=gallery_token_data.model_dump())
        response = HttpResponseRedirect(redirect_to)
        response.set_cookie("session", gallery_access_token)
        return response

    
    def log_out(self, redirect_to: str="/about"):
        response = HttpResponseRedirect(redirect_to=redirect_to)
        response.delete_cookie("session")
        return response

    def login_required(self):
        def __outer_wrapper__(func):
            def __inner_wrapper__(request: HttpRequest,*args, **kargs):
                try:
                    token_data = self.authenticate_request(request=request)    
                    request.user.token_data = token_data
                    user_data = self.user_db_service.search_user(token_data.auth_token,
                                                                 search_value=token_data.sub)
                    request.user.id = user_data.user_id

                    view_response = func(request, *args, **kargs)

                    return view_response
                except PermissionError as err:
                    response = HttpResponseRedirect(self.login_redirect_path)
                    response.set_cookie("session", "Expired")
                    return response
            return __inner_wrapper__
        return __outer_wrapper__

    def is_authenticated(self):
        def __outer_wrapper__(func):
            def __inner_wrapper__(request: HttpRequest,*args,**kargs):
                try:
                    token_data = self.authenticate_request(request=request)
                    request.user.token_data = token_data
                    user_data = self.user_db_service.search_user(token_data.auth_token,
                                                                    search_value=token_data.sub)
                    request.user.id = user_data.user_id
                except Exception:
                    pass

                view_response = func(request, *args, **kargs)

                return view_response
            return __inner_wrapper__
        return __outer_wrapper__



    def authenticate_request(self, request: HttpRequest):
        session_token = request.COOKIES.get("session")
        if session_token is None:
            raise ValueError("No valid session")
        return self.__get_data_from_token__(session_token)

    def __get_data_from_token__(self, token: str) -> TokenData:
        credentials_exception = PermissionError("Invalid Session Token")
        try:
            payload = jwt.decode(token, self.__get_jwt_key__(), algorithms=[self.jwt_algorithm])
            username: str = payload.get("sub")
            auth_token: str = payload.get("auth_token")
            if username is None or auth_token is None:
                raise credentials_exception
            token_data = TokenData(sub=username, auth_token=Token(**auth_token))
            return token_data
        except JWTError:
            raise credentials_exception
    
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
    
    def __get_jwt_key__(self):
        with open(self.jwt_key_location, 'r') as file:
            temp_token = file.read()
        return temp_token
