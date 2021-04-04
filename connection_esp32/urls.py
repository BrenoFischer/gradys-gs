from django.urls import path

from .views import index, connection

urlpatterns = [
    path('', index),
    path('connection/', connection)
]
