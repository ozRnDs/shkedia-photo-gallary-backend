import traceback
import logging
logger = logging.getLogger(__name__)

from typing import Dict, List

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.contrib import messages

from business.config import app_config
from business.gallery.service import MediaGalleryService ,SearchResult, Insight
from business.authentication.service import AuthService
from business.db.media_service import MediaDBService
from business.encryption.service import DecryptService
from business.db.user_service import UserDBService
from business.db.insights_service import InsightEngineService
from business.gallery.media_service import MediaViewService

debug_mode = False if app_config.DEBUG == 0 else True

# Create your views here.
decrypt_service = DecryptService(private_key_location=app_config.PRIVATE_KEY_LOCATION)
media_db_service = MediaDBService(host=app_config.MEDIA_DB_HOST, port=app_config.MEDIA_DB_PORT)
user_db_service = UserDBService(host=app_config.USER_DB_HOST, port=app_config.USER_DB_PORT)

engine_service = InsightEngineService(db_media_service=media_db_service)
auth_service = AuthService(db_user_service=user_db_service,
                           jwt_key_location=app_config.JWT_KEY_LOCATION,
                            )
gallery_service = MediaGalleryService(decrypt_service=decrypt_service,
                                      user_db_service=user_db_service,
                                      media_db_service=media_db_service,
                                      local_cache_location=app_config.LOCAL_CACHE_LOCATION,
                                      debug_mode=debug_mode)
media_service = MediaViewService(media_db_service=media_db_service,
                                 decrypt_service=decrypt_service,
                                 user_db_service=user_db_service,
                                 engine_service=engine_service)

def login_page(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            return auth_service.log_in(username=username, password=password, redirect_to="/")
        except PermissionError:
            messages.add_message(request, messages.ERROR, "Wrong username or password")
        except Exception:
            traceback.print_exc()
            messages.add_message(request, messages.ERROR, "Sorry, I'm not sure what went wrong")

    if request.COOKIES.get("session") == "Expired":
        messages.add_message(request, messages.INFO, "Your session expired. Please log in again.")
        
    context= { "login_needed": True}
    response = render(request, 'base/login.html', context)
    if request.COOKIES.get("session") == "Expired":
        response.delete_cookie("session")
    return response

def logout_page(request: HttpRequest):
    return auth_service.log_out()


@auth_service.login_required()
def home(request: HttpRequest):

    return albums(request, page_number=1)

@auth_service.login_required()
def albums(request: HttpRequest, page_number):


    # gallery_service.__refresh_cache__(token=request.user.token_data.auth_token,
    #                                   user_id=request.user.id)
    
    engine_type = request.GET.get("engine_type") if request.GET.get("engine_type") else "months"

    try:
        album_list: SearchResult = gallery_service.get_collections_for_user(token=request.user.token_data.auth_token,engine_type=engine_type, page_number=page_number-1)
    except PermissionError as err:
        return HttpResponseRedirect(redirect_to="/login")
    except ConnectionError as err:
        return HttpResponseRedirect(redirect_to="/about?error=connection")

    # page_object = gallery_service.get_page_content(album_list, page_number)
    if album_list.total_results_number==0:
        return HttpResponseNotFound(content="Couldn't find collections for engine")

    if page_number > album_list.number_of_pages:
        return albums(request, album_list.number_of_pages)

    context = {
        "engine_type": engine_type,
        "album_list": album_list.results,
        "page": page_number,
        "pages_list": range(1,album_list.number_of_pages+1),
        "search_needed": True
    }

    return render(request, 'base/albums.html', context)

@auth_service.login_required()
def view_album(request: HttpRequest, engine_type, collection_name, page_number):
    album_list = None
    try:
        album_list: SearchResult = gallery_service.get_collections_for_user(token=request.user.token_data.auth_token,engine_type=engine_type, page_number=0, page_size=10)
    except Exception:
        pass
    try:
        collection, page_object = gallery_service.get_collection_for_user(token=request.user.token_data.auth_token, collection_name=collection_name, engine_type=engine_type, page_number=page_number-1)
    except FileNotFoundError as err:
        return HttpResponseNotFound(content=str(err))
    except PermissionError as err:
        return HttpResponseRedirect(redirect_to="/login")
    
    context = {
        "engine_type": engine_type,
        "view_type": "album",
        "nav_list": album_list.results,
        "album_name": collection.name,
        "media_list": gallery_service.decrypt_list_of_medias(page_object.items),
        "page": page_number,
        "pages_list": range(1,page_object.number_of_pages+1),
        "search_needed": True
    }

    return render(request, 'base/view_album.html', context)

@auth_service.login_required()
def view_media(request, engine_type, collection_name, page_number, media_id):
    try:
        media_item = media_service.get_media_content(token=request.user.token_data.auth_token,
                                                    media_id=media_id, user_id=request.user.id)
    except FileNotFoundError as err:
        return HttpResponseNotFound(content=str(err))
    except PermissionError as err:
        return HttpResponseRedirect(redirect_to="/login")
    try:
        collection, nav_object = gallery_service.get_collection_for_user(token=request.user.token_data.auth_token, collection_name=collection_name, engine_type=engine_type, page_number=page_number-1)
    except Exception as err:
        logger.warning(f"Failed to get nav content: {str(err)}")
    grouped_insights: None | Dict[str,Dict[str,List[Insight]]] = None
    try:
        grouped_insights = media_service.get_media_insights(token=request.user.token_data.auth_token,media_id=media_id)
    except Exception as err:
        logger.warning(f"Failed to get insights: {str(err)}")
    context = {
        "nav_list": gallery_service.decrypt_list_of_medias(nav_object.items),
        "view_type": "media",
        "media": media_item,
        "album_name": collection_name,
        "engine_type": engine_type,
        "page": page_number,
        "search_needed": True,
        "grouped_insights": grouped_insights
    }
    
    return render(request, 'base/view_media.html', context)

    return HttpResponse(f"This is media number: {media_id}")

@auth_service.is_authenticated()
def about(request):
    return render(request, 'base/about.html', {})

@auth_service.is_authenticated()
def about_creator(request):
    return render(request, 'base/about_creator.html', {})