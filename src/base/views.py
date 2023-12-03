from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect

from business.config import app_config
from business.gallery.service import MediaGalleryService ,Album, MediaView
from business.authentication.service import Token, AuthService
from business.db.media_service import MediaDBService
from business.encryption.service import DecryptService
from business.db.user_service import UserDBService, UserRequest
from typing import List

# Create your views here.
decrypt_service = DecryptService(private_key_location=app_config.PRIVATE_KEY_LOCATION)
media_db_service = MediaDBService(host=app_config.MEDIA_DB_HOST, port=app_config.MEDIA_DB_PORT)
user_db_service = UserDBService(host=app_config.USER_DB_HOST, port=app_config.USER_DB_PORT)
auth_service = AuthService(db_user_service=user_db_service,
                           jwt_key_location=app_config.JWT_KEY_LOCATION,
                            )
gallery_service = MediaGalleryService(decrypt_service=decrypt_service,
                                      user_db_service=user_db_service,
                                      media_db_service=media_db_service,
                                      local_cache_location=app_config.LOCAL_CACHE_LOCATION)

def login_page(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        return auth_service.log_in(username=username, password=password, redirect_to="/")


        
    context= { "login_needed": True}
    return render(request, 'base/login.html', context)

def logout_page(request: HttpRequest):
    return auth_service.log_out()


@auth_service.login_required()
def home(request: HttpRequest):

    return albums(request, page_number=1)

@auth_service.login_required()
def albums(request: HttpRequest, page_number):

    # token = request.headers.get("Auzthorization")
    token = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJleHAiOjE3MDE1MjM5MzJ9.HICNe2oTdph55YRxXZFnKQcFsDs1lMdMkA3C4pdgqSY",
            "token_type": "bearer"
            }
    gallery_service.__refresh_cache__(token=Token(**token),
                                      user_id="8c0e1d9d-9ade-4881-9196-e9ae2c33383f")
    
    album_list: List[Album] = gallery_service.albums_list

    page_object = gallery_service.get_page_content(album_list, page_number)

    if page_number > page_object.number_of_pages:
        return albums(request, page_object.number_of_pages)

    context = {
        "album_list": page_object.items,
        "page": page_number,
        "pages_list": range(1,page_object.number_of_pages+1),
        "search_needed": True
    }

    return render(request, 'base/albums.html', context)

@auth_service.login_required()
def view_album(request: HttpRequest, album_name, page_number):

    chosen_album = [album for album in gallery_service.albums_list if album.name == album_name][-1]

    page_object = gallery_service.get_page_content(chosen_album.images_list, page_number)


    context = {
        "album_name": album_name,
        "media_list": gallery_service.decrypt_list_of_medias(page_object.items),
        "page": page_number,
        "pages_list": range(1,page_object.number_of_pages+1),
        "search_needed": True
    }

    return render(request, 'base/view_album.html', context)

@auth_service.login_required()
def view_media(request, album_name, page_number, media_id):

    context = {
        "media": gallery_service.get_media_content(media_id=media_id),
        "album_name": album_name,
        "page_number": page_number,
        "search_needed": True
    }
    
    return render(request, 'base/view_media.html', context)

    return HttpResponse(f"This is media number: {media_id}")

@auth_service.is_authenticated()
def about(request):
    return render(request, 'base/about.html', {})