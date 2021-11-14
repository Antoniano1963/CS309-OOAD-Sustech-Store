from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from . import views

urlpatterns = [
    # url('user_mobile_homepage/', views.user_mobile_homepage),
    url('start_dialogue/', views.start_dialogue),
    url('begin_websocket/', views.begin_websocket),
    url('dialogue_detail/', views.dialogue_detail),
    url('dialogue_list/', views.dialogue_list),
]
