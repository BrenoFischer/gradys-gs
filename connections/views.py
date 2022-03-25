import json

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync

from .consumers_wrapper.post_consumers import get_post_consumer_instance
from .consumers_wrapper.update_periodically_consumer import get_device_from_list_by_id
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


def index(request):
  context = {
    'google_maps_key': settings.GOOGLE_MAPS_API_KEY,
    'server_address': config['server']['ip']
  }
  return render(request, 'index.html', context=context)


def create_new_dict(request_received):
  ip = config['post']['ip']

  new_dict = {}
  new_dict['id'] = int(request_received.POST.get('id'))
  new_dict['type'] = int(request_received.POST.get('type'))
  new_dict['seq'] = int(request_received.POST.get('seq'))
  new_dict['lat'] = float(request_received.POST.get('lat'))
  new_dict['lng'] = float(request_received.POST.get('lng'))
  new_dict['alt'] = float(request_received.POST.get('alt'))
  new_dict['device'] = request_received.POST.get('device')
  
  if request_received.POST.get('ip') != None:
    new_dict['ip'] = request_received.POST.get('ip')
  else:
    print('Não há ip base')
    new_dict['ip'] = ip
  return new_dict


@csrf_exempt 
@async_to_sync
async def post_to_socket(request):
  # Receives a POST request with information on it's body
  # Start ACK with an error code on type (101?).
  # If the post is sent to the consumer, the type is 103.
  ack = {"id": 1, "type": 101, "seq": 0, "lat": 0, "lng": 0, "alt": 0, "DATA": "0"}

  if request.method == 'POST':
    new_dict = create_new_dict(request)

    post_consumer_instance = get_post_consumer_instance()
    if post_consumer_instance is not None:
      await post_consumer_instance.receive_post(new_dict)
      ack['type'] = 103

  return JsonResponse(ack)

@csrf_exempt
def send_uav_ip(request):
  # Receives a POST request with the ID of an uav
  # Search the uav IP on the permanente devices list and send it back

  if request.method == 'POST':
    id = json.load(request)['id']
  else:
    print(f'No POST request {request.POST}')
    id = 'all'
  
  device = get_device_from_list_by_id(id)
  if id == 'all':
    ip = config['server']['ip']
  else:
    ip = device['ip']
  
  return JsonResponse({'ip': ip})
