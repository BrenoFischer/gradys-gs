import configparser
import json
from django.urls import path

from .views import index, connection, post_to_socket, receive_command_test

config = configparser.ConfigParser()
config.read('config.ini')
base_path = str(config['post']['base_path'])

urlpatterns = [
    path('', index),
    path('connection/', connection),
    path('update-drone/', post_to_socket),
    path('<int:device_id>/' + base_path, receive_command_test),
]
