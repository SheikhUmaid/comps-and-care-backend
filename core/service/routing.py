from service.consumers import ServiceRequestConsumer
from django.urls import re_path



websocket_urlpatterns = [
    re_path(r'^ws/service/(?P<pk>\w+)/$', ServiceRequestConsumer.as_asgi()),
]