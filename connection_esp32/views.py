from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync

from .consumers_wrapper.post_consumers import get_post_consumer_instance
import configparser


def index(request):
  context = {
    'google_maps_key': settings.GOOGLE_MAPS_API_KEY
  }
  return render(request, 'index.html', context=context)


def create_new_dict(request_received):
  config = configparser.ConfigParser()
  config.read('config.ini')

  ip = config['post']['ip']

  new_dict = {}
  new_dict['id'] = int(request_received.POST.get('id'))
  new_dict['type'] = int(request_received.POST.get('type'))
  new_dict['seq'] = int(request_received.POST.get('seq'))
  new_dict['lat'] = float(request_received.POST.get('lat'))
  new_dict['log'] = float(request_received.POST.get('log'))
  new_dict['high'] = float(request_received.POST.get('high'))
  new_dict['DATA'] = request_received.POST.get('DATA')
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
  # Start ACK with an error code on type (101?).
  # If the post is sent to the consumer, the type is 103.
  ack = {"id": 1, "type": 101, "seq": 0, "lat": 0, "log": 0, "high": 0, "DATA": "0"}

  if request.method == 'POST':
    new_dict = create_new_dict(request)

    post_consumer_instance = get_post_consumer_instance()
    if post_consumer_instance is not None:
      await post_consumer_instance.receive_post(new_dict)
      ack['type'] = 103

  return JsonResponse(ack)


@csrf_exempt
def receive_command_test(request, device_id):
  # View temporária simulando um UAV como servidor web, que irá receber um comando da GS
  ack = {"id": 1, "type": -1, "seq": 0, "lat": 0, "log": 0, "high": 0, "DATA": "0"}
  
  if request.method == 'POST':
    type = int(request.POST.get('type'))
    print(f'O device com id: {device_id} recebeu o comando {type}')
    if type == 24:
      ack['type'] = 25
    if type == 26:
      ack['type'] = 27
    if type == 28:
      ack['type'] = 29
    if type == 30:
      ack['type'] = 31

  return JsonResponse(ack)


@csrf_exempt
def send_info_from_get(request, device_id):
  # View temporária simulando um UAV como servidor web, que irá enviar um comando para GS
  ack = {"id": 1, "type": -1, "seq": 0, "lat": 0, "log": 0, "high": 0, "DATA": "0"}
  if request.method == 'GET':
    print(f'O device com id: {device_id} está retornando informações.')
    ack['id'] = device_id

  return JsonResponse(ack)
