from django.shortcuts import render
from django.conf import settings


def index(request):
  return render(request, 'index.html', context={})

def connection(request):
  context = {
    'google_maps_key': settings.GOOGLE_MAPS_API_KEY
  }
  return render(request, 'connection.html', context=context)