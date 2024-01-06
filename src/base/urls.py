from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),

    path('about', views.about, name="about"),
    path('about/media', views.about_creator, name="about_creator"),
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_page, name="logout"),

    path('collections/<str:engine_type>/<int:page_number>', views.albums, name="albums"),
    path('collections/<str:engine_type>/<str:collection_name>/<int:page_number>', views.view_album, name="album_view"),
    
    path('medias/<str:engine_type>/<str:collection_name>/<int:page_number>/<str:media_id>', views.view_media, name="media_view"),
]