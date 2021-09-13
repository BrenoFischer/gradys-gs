import configparser
from django.urls import path

from .views import index, post_to_socket, receive_command_test, send_info_from_get

config = configparser.ConfigParser()
config.read('config.ini')

# Path to receive POST request, with updated info, from a device
path_receive_info = config['post']['path_receive_info']

# Base path to simulate device that will send info from a GET request
base_path_get = config['get']['base_get_path']

urlpatterns = [
    path('', index),
    path(path_receive_info, post_to_socket),
    path('<int:command>/', receive_command_test),
    path('<int:device_id>/' + base_path_get, send_info_from_get),
]
