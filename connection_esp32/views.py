from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .consumers import get_post_consumer_instance
from django.views.decorators.csrf import csrf_exempt


def index(request):
  return render(request, 'index.html', context={})

def connection(request):
  context = {
    'google_maps_key': settings.GOOGLE_MAPS_API_KEY
  }
  return render(request, 'connection.html', context=context)

def create_new_dict(request_received):
  new_dict = {}
  new_dict['id'] = int(request_received.POST.get('id'))
  new_dict['type'] = int(request_received.POST.get('type'))
  new_dict['seq'] = int(request_received.POST.get('seq'))
  new_dict['lat'] = float(request_received.POST.get('lat'))
  new_dict['log'] = float(request_received.POST.get('log'))
  new_dict['high'] = float(request_received.POST.get('high'))
  new_dict['DATA'] = request_received.POST.get('DATA')
  return new_dict

@csrf_exempt 
def post_to_socket(request):
  if request.method == 'POST':
    new_dict = create_new_dict(request)

    post_consumer_instance = get_post_consumer_instance()
    post_consumer_instance.receive_post(new_dict)

  return JsonResponse({'status_code':'ok'})