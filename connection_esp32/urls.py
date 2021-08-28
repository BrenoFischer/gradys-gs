import configparser
from django.urls import path

from .views import index, connection, post_to_socket, receive_command_test, send_info

config = configparser.ConfigParser()
config.read('config.ini')
base_path = str(config['post']['base_path'])
base_path_get = str(config['get']['base_get_path'])

urlpatterns = [
    path('', index),
    path('connection/', connection),
    path('update-drone/', post_to_socket),
    path('<int:device_id>/' + base_path, receive_command_test),
    path('<int:device_id>/' + base_path_get, send_info),
]
