from django.urls import path
from .consumers import ConnectionConsumer


ws_urlpatterns = [
  path('ws/connection/', ConnectionConsumer.as_asgi())
]