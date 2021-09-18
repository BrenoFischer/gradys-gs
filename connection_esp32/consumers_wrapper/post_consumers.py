import logging
import aiohttp
import asyncio
import json
import configparser
from datetime import date, datetime
from .update_periodically_consumer import get_device_from_list_by_id, append_device_to_persistant_list
from channels.generic.websocket import AsyncWebsocketConsumer

from ..utils.logger import Logger


class PostConsumer(AsyncWebsocketConsumer):
  # Websocket consumer that handles POST requests received.
  # The 'post_to_socket' VIEW receive the request, call 'receive_post' method from this class and send it to JS.
  # Receive msgs from JS, with the 'receive' method and send it to the specific device(s) with HTTP request (POST or GET)

  def __init__(self) -> None:
      super().__init__()
      self.async_tasks = []


  async def connect(self):
    # Called when websocket connection is required (when corresponding url is accessed).
    global post_consumer_instance
    await self.accept()
    # Instantiate itself, so 'post_to_socket' view can access this class method.
    post_consumer_instance = self


  async def disconnect(self, close_code):
    # Called when websocket connection is closed.
    for task in self.async_tasks:
      task.cancel()
    print(f'Post websocket disconnected {close_code}')


  async def send_post_specific_device(self, url, json_to_send):
    # Send POST request to specific URL (representing a specific device)
    async with aiohttp.ClientSession() as session:
      # --- (Temporary test) Delay to test parallel tasks (device id 5 wait 5s to send) ---
      device_id = json_to_send['id']
      if device_id == '5':
        await asyncio.sleep(5)
      # --- (End of temporary test) ---
      print(f'Enviando: {json_to_send}')
      async with session.post(url, data=json_to_send) as resp:
        response = await resp.json() 


  async def send_get_specific_device(self, url):
    # Send GET request to specific URL (representing a specific device), wait for response and send to JS via socket
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
        response_from_device = await resp.json() 
        print(f'Django recebeu resposta do GET request: {response_from_device}')

        logger.log_info(source=response_from_device['device'], data=response_from_device)
        await self.send(json.dumps(response_from_device))


  async def send_via_http(self, text_data):
    # The command received via socket will be processed 
    received_json = json.loads(text_data)

    # It'll search the 'persistent device list' for available device, with matching id,
    # Or get all persistent list if device_receiver_id is 'all'.
    device_receiver_id = str(received_json['receiver'])
    device_to_send_list = get_device_from_list_by_id(device_receiver_id)

    for device in device_to_send_list:
      ip = device['ip']
      id = str(device['id'])
      url = ip + str(received_json['type']) + '/'
      # Json_to_send will have the correct ID in the 'id' field
      json_to_send = replicate_dict_new_id(id, received_json)

      if received_json['type'] == command_to_get:
        # The command is a GET request and will have the 'view' GET base_path
        url = ip + id + '/' + base_path_get
        task = asyncio.create_task(self.send_get_specific_device(url))
      else:
        # POST request
        task = asyncio.create_task(self.send_post_specific_device(url, json_to_send))
      self.async_tasks.append(task)


  async def receive(self, text_data):
    # Receive msg (text_data) from socket and call 'send_via_http' method to handle it 
    logger.log_info(source="GS", data=text_data)
    
    await self.send_via_http(text_data)


  async def receive_post(self, data):
    # Called from 'post_to_socket' view, when a POST arrives from a device
    data['method'] = 'post'
    data['time'] = get_time_now().replace('"', '')
    data['status'] = 'active'

    append_device_to_persistant_list(data)

    logger.log_info(source=data['device'], data=data)
    try:
      await self.send(json.dumps(data)) # Send to JS via socket
    except Exception:
      logger.log_except()



# Auxiliary functions
# -------------------
def get_post_consumer_instance():
  global post_consumer_instance
  return post_consumer_instance


def get_time_now():
  return json.dumps(datetime.now(), default=json_serializer)


def json_serializer(obj):
  # Function to help formatting 
  if isinstance(obj, (datetime, date)):
    return obj.isoformat()
  raise TypeError ("Type %s not serializable" % type(obj))


def replicate_dict_new_id(id, json_to_send):
  # Create a new dict changing it's 'ID' key
  new_dict = {}
  for key, item in json_to_send.items():
    if key == 'id':
      new_dict[key] = id
    else:
      new_dict[key] = item
  return new_dict
# End of Auxiliary functions
# -------------------


# --- Pre-process to get .ini info ---
config = configparser.ConfigParser()
config.read('config.ini')

base_path_get = config['get']['base_get_path']
command_to_get = int(config['get']['command_type'])
# --- End of pre-processing ---

post_consumer_instance = None
logger = Logger()
