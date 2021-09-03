import logging
import aiohttp
import asyncio
import json
import configparser
from datetime import date, datetime
from .update_periodically_consumer import get_device_from_list_by_id, append_json_to_list
from channels.generic.websocket import AsyncWebsocketConsumer


class PostConsumer(AsyncWebsocketConsumer):
  def __init__(self) -> None:
      super().__init__()
      self.logger_except = None
      self.logger_info = None
      self.tasks = []

  async def connect(self):
    global post_consumer_instance
    await self.accept()
    self.initiate_loggers()
    post_consumer_instance = self
  
  async def send_post_especific_device(self, url, json_to_send):
    async with aiohttp.ClientSession() as session:
      device_id = url.split('/')[3]
      if device_id == '5':
        await asyncio.sleep(5)
      async with session.post(url, data=json_to_send) as resp:
        response = await resp.json() 
        #print(f'ACK: {response}')

  async def send_get_especific_device(self, url):
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
        response_from_device = await resp.json() 
        print(f'Django recebeu resposta do GET request: {response_from_device}')
        if self.logger_info != None:
          self.logger_info.info(response_from_device)
        await self.send(json.dumps(response_from_device))

  async def send_via_post(self, text_data):
    config = configparser.ConfigParser()
    config.read('config.ini')
    received_json = json.loads(text_data)

    base_path = config['post']['base_path']
    base_path_get = config['get']['base_get_path']
    device_id = str(received_json['receiver'])

    device_to_send = get_device_from_list_by_id(device_id)

    if device_to_send is None:
      print('Não tem pra quem mandar')
    else:
      command_to_get = int(config['get']['command_type'])

      if device_id == 'all':
        for device in device_to_send:
          if device['status'] != 'inactive':
            ip = device['ip']
            id = str(device['id'])
            url = ip + id + '/' + base_path
            if received_json['type'] == command_to_get: #GET request
              url = ip + id + '/' + base_path_get
              task = asyncio.create_task(self.send_get_especific_device(url))
            else:
              task = asyncio.create_task(self.send_post_especific_device(url, received_json))
            self.tasks.append(task)
      else:
        if device_to_send['status'] != 'inactive':
          ip = device_to_send['ip']
          url = ip + device_id + '/' + base_path

          if received_json['type'] == command_to_get: #GET request
            url = ip + device_id + '/' + base_path_get
            
            await self.send_get_especific_device(url)
          else:  
            await self.send_post_especific_device(url, received_json)
  

  async def receive(self, text_data):
    if self.logger_info != None:
      self.logger_info.info(text_data)
    
    await self.send_via_post(text_data)

  async def receive_post(self, data):
    data['method'] = 'post'
    data['time'] = get_time().replace('"', '')
    data['status'] = 'active'

    append_json_to_list(data)

    if self.logger_info != None:
      self.logger_info.info(data)
    try:
      await self.send(json.dumps(data))
    except Exception:
      if self.logger_except != None:
        self.logger_except.exception('')

  async def disconnect(self, close_code):
    for task in self.tasks:
      task.cancel()
    print(f'Post websocket disconnected {close_code}')

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



# Auxiliary functions
# -------------------
def get_post_consumer_instance():
  global post_consumer_instance
  return post_consumer_instance


def get_time():
  return json.dumps(datetime.now(), default=json_serializer)


def json_serializer(obj):
  if isinstance(obj, (datetime, date)):
    return obj.isoformat()
  raise TypeError ("Type %s not serializable" % type(obj))


post_consumer_instance = None
