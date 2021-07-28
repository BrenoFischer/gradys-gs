from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .consumers import get_post_consumer_instance
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async


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
  new_dict['device'] = request_received.POST.get('device')
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
def receive_command_test(request):
  # View temporária simulando um UAV como servidor web, que irá receber um comando da GS
  ack = {"id": 1, "type": -1, "seq": 0, "lat": 0, "log": 0, "high": 0, "DATA": "0"}
  
  if request.method == 'POST':
    #print('Recebeu comando no UAV!')
    type = int(request.POST.get('type'))
    if type == 24:
      ack['type'] = 25
    if type == 26:
      ack['type'] = 27
    if type == 28:
      ack['type'] = 29
    if type == 30:
      ack['type'] = 31

  return JsonResponse(ack)
