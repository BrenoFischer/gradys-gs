from django.urls import path

from .views import index, connection, post_to_socket, receive_command_test

urlpatterns = [
    path('', index),
    path('connection/', connection),
    path('update-drone/', post_to_socket),
    path('receive-command-test/', receive_command_test)
]
