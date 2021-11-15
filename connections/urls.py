import configparser
from django.urls import path

from .views import index, post_to_socket, receive_command_test

config = configparser.ConfigParser()
config.read('config.ini')

# Path to receive POST request, with updated info, from a device
path_receive_info = config['post']['path_receive_info']


urlpatterns = [
    path('', index),
    path(path_receive_info, post_to_socket),
    path('<int:command>/', receive_command_test),
]
