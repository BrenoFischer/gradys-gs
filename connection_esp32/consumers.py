import json
from datetime import date, datetime
from .serial_connector import SerialConnection

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer

class ReceiveCommandConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

  async def receive(self, text_data):
    if async_serial.is_connected:
      await async_serial.aio_instance.write_async(text_data.encode())

  async def disconnect(self, close_code):
    print(f'Receive command websocket disconnected {close_code}')


class ConnectionConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()
    #async_serial.initiate_loggers()
    await async_serial.start_serial_connection(self)

  async def disconnect(self, close_code):
    print(f'Connection websocket disconnected {close_code}')


class PostConsumer(WebsocketConsumer):
  def connect(self):
    global post_consumer_instance
    self.accept()
    post_consumer_instance = self

  def receive_post(self, data):
    data['method'] = 'post'
    data['time'] = get_time()
    #print(data)
    append_json_to_list(data, json_list_persistent)
    self.send(json.dumps(data))

  def disconnect(self, close_code):
    print(f'Post websocket disconnected {close_code}')


def get_post_consumer_instance():
  global post_consumer_instance
  return post_consumer_instance

def get_json_list_persistent():
  global json_list_persistent
  return json_list_persistent

def json_serializer(obj):
  if isinstance(obj, (datetime, date)):
    return obj.isoformat()
  raise TypeError ("Type %s not serializable" % type(obj))

def get_time():
  return json.dumps(datetime.now(), default=json_serializer)

def append_json_to_list(data, json_list):
  drone_already_on_array = False
  for i,drone in enumerate(json_list):
    if drone['id'] == data['id']:
      drone_already_on_array = True
      if drone['time'] < data['time']:
        json_list.pop(i)
        json_list.append(data)
      break

  if not drone_already_on_array:
    json_list.append(data)

  print(json_list)


json_list_persistent = []

async_serial = SerialConnection()
post_consumer_instance = None
