from django.urls import re_path
from django.conf.urls import url
from . import consumers
websocket_urlpatterns = [
    re_path(r'api/ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
