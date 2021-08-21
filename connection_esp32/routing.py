from django.urls import path
from .consumers import ConnectionConsumer, ReceiveCommandConsumer, PostConsumer, UpdatePeriodcallyConsumer


ws_urlpatterns = [
  path('ws/connection/', ConnectionConsumer.as_asgi()),
  path('ws/receive/', ReceiveCommandConsumer.as_asgi()),
  path('ws/update-info/', PostConsumer.as_asgi()),
  path('ws/update-periodically/', UpdatePeriodcallyConsumer.as_asgi())
]