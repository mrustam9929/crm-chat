from django.urls import re_path

from ws import consumers

websocket_urlpatterns = [
    re_path(r'connect/$', consumers.WsChatConsumer.as_asgi()),
]
