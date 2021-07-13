from django.urls import path

from .views import index, connection, post_to_socket

urlpatterns = [
    path('', index),
    path('connection/', connection),
    path('update-drone/', post_to_socket)
]
