import configparser
import json
from django.urls import path

from .views import index, connection, post_to_socket, receive_command_test1, receive_command_test2, receive_command_test3, receive_command_test4, receive_command_test5

config = configparser.ConfigParser()
config.read('config.ini')
paths = json.loads(config.get('post','paths'))

urlpatterns = [
    path('', index),
    path('connection/', connection),
    path('update-drone/', post_to_socket),
    path(paths[0], receive_command_test1),
    path(paths[1], receive_command_test2),
    path(paths[2], receive_command_test3),
    path(paths[3], receive_command_test4),
    path(paths[4], receive_command_test5)
]
