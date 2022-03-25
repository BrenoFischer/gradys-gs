from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync

from .consumers_wrapper.post_consumers import get_post_consumer_instance
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
def receive_command_test(request, command):
  # View temporária simulando um UAV como servidor web, que irá receber um comando da GS
  ack = {"id": 1, "type": -1, "seq": 0, "lat": 0, "lng": 0, "alt": 0, "DATA": "0"}
  
  if request.method == 'POST':
    device_id = int(request.POST.get('id'))
    print(f'O device com id: {device_id} recebeu o comando {command}')
    if command == 24:
      ack['type'] = 25
    if command == 26:
      ack['type'] = 27
    if command == 28:
      ack['type'] = 29
    if command == 30:
      ack['type'] = 31

  return JsonResponse(ack)
