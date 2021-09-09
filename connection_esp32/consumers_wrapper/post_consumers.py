import logging
import aiohttp
import asyncio
import json
import configparser
from datetime import date, datetime
from .update_periodically_consumer import get_device_from_list_by_id, append_device_to_persistant_list
from channels.generic.websocket import AsyncWebsocketConsumer


class PostConsumer(AsyncWebsocketConsumer):
  # Websocket consumer that handles POST requests received.
  # The 'post_to_socket' VIEW receive the request, call 'receive_post' method from this class and send it to JS.
  # Receive msgs from JS, with the 'receive' method and send it to the specific device(s) with HTTP request (POST or GET)

  def __init__(self) -> None:
      super().__init__()
      self.logger_except = None
      self.logger_info = None
      self.async_tasks = []


  async def connect(self):
    # Called when websocket connection is required (when corresponding url is accessed).
    global post_consumer_instance
    await self.accept()
    self.initiate_loggers()
    # Instantiate itself, so 'post_to_socket' view can access this class method.
    post_consumer_instance = self


  async def disconnect(self, close_code):
    # Called when websocket connection is closed.
    for task in self.async_tasks:
      task.cancel()
    print(f'Post websocket disconnected {close_code}')


  async def send_post_especific_device(self, url, json_to_send):
    # Send POST request to specific URL (representing a specific device)
    async with aiohttp.ClientSession() as session:
      # --- (Temporary test) Delay to test parallel tasks (device id 5 wait 5s to send) ---
      device_id = url.split('/')[3]
      if device_id == '5':
        await asyncio.sleep(5)
      # --- (End of temporary test) ---
      async with session.post(url, data=json_to_send) as resp:
        response = await resp.json() 


  async def send_get_especific_device(self, url):
    # Send GET request to specific URL (representing a specific device), wait for response and send to JS via socket
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
        response_from_device = await resp.json() 
        print(f'Django recebeu resposta do GET request: {response_from_device}')
        if self.logger_info != None:
          self.logger_info.info(response_from_device)
        await self.send(json.dumps(response_from_device))


  async def send_via_http(self, text_data):
    # The command received via socket will be processed 
    # --- Pre-process to get .ini info ---
    config = configparser.ConfigParser()
    config.read('config.ini')
    received_json = json.loads(text_data)

    base_path = config['post']['base_path_uav']
    base_path_get = config['get']['base_get_path']
    command_to_get = int(config['get']['command_type'])
    # --- End of pre-processing ---

    # It'll search the 'persistent device list' for available device, with matching id,
    # Or get all persistent list if device_id is 'all'.
    device_id = str(received_json['receiver'])
    device_to_send = get_device_from_list_by_id(device_id)

    if device_to_send is None:
      print('There is no available device to send.')
    else:
      if device_id == 'all':
        for device in device_to_send:
          if device['status'] != 'inactive':
            ip = device['ip']
            id = str(device['id'])
            url = ip + id + '/' + base_path
            if received_json['type'] == command_to_get:
              # The command it's a GET request and will have the 'view' GET base_path
              url = ip + id + '/' + base_path_get
              task = asyncio.create_task(self.send_get_especific_device(url))
            else:
              # POST request
              task = asyncio.create_task(self.send_post_especific_device(url, received_json))
            self.async_tasks.append(task)
      else: # Request for specific device id
        if device_to_send['status'] != 'inactive':
          ip = device_to_send['ip']
          url = ip + device_id + '/' + base_path

          if received_json['type'] == command_to_get:
            # GET request
            url = ip + device_id + '/' + base_path_get
            await self.send_get_especific_device(url)
          else:
            # POST request
            await self.send_post_especific_device(url, received_json)
  

  async def receive(self, text_data):
    # Receive msg (text_data) from socket and call 'send_via_http' method to handle it 
    if self.logger_info != None:
      self.logger_info.info(text_data)
    
    await self.send_via_http(text_data)


  async def receive_post(self, data):
    # Called from 'post_to_socket' view, when a POST arrives from a device
    data['method'] = 'post'
    data['time'] = get_time_now().replace('"', '')
    data['status'] = 'active'

    append_device_to_persistant_list(data)

    if self.logger_info != None:
      self.logger_info.info(data)
    try:
      await self.send(json.dumps(data)) # Send to JS via socket
    except Exception:
      if self.logger_except != None:
        self.logger_except.exception('')


  # --- Logging functions ---
  def setup_logger(self, name, log_file, my_format, level=logging.INFO):
    formatter = logging.Formatter(my_format)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    lo = logging.getLogger(name)
    lo.setLevel(level)
    lo.addHandler(handler)

    return lo


  def initiate_loggers(self):
    time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = "./connection_esp32/LOGS/"

    log_file_name_exc = path + f'exceptions/post-{time_now}.log'
    self.logger_except = self.setup_logger('log_exception', log_file_name_exc, '%(lineno)d: %(asctime)s %(message)s', level=logging.ERROR)

    log_file_name_info = path + f'info/post-{time_now}.log'
    self.logger_info = self.setup_logger('log_info', log_file_name_info, '%(asctime)s %(message)s', level=logging.INFO)
  # --- End of Logging functions ---


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
# End of Auxiliary functions
# -------------------

post_consumer_instance = None
