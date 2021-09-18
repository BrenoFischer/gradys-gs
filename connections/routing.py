from django.urls import path
from .consumers_wrapper.post_consumers import  PostConsumer
from .consumers_wrapper.update_periodically_consumer import UpdatePeriodcallyConsumer
from .consumers_wrapper.serial_consumers import ConnectionConsumer, ReceiveCommandConsumer

ws_urlpatterns = [
  path('ws/connection/', ConnectionConsumer.as_asgi()),
  path('ws/receive/', ReceiveCommandConsumer.as_asgi()),
  path('ws/update-info/', PostConsumer.as_asgi()),
  path('ws/update-periodically/', UpdatePeriodcallyConsumer.as_asgi())
]