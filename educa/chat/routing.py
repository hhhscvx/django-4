from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/room/(?P<course_id>\d+)/$',  # ws/chat/room/<course_id>
            consumers.ChatConsumer.as_asgi()),  # как as_view()
]
