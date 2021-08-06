import json
import asyncio
import logging
import aiohttp
import configparser
from datetime import date, datetime, timedelta
from .serial_connector import SerialConnection

from channels.generic.websocket import AsyncWebsocketConsumer

# Consumers
#--------------
class ReceiveCommandConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

  async def receive(self, text_data):
    if async_serial != None:
      if async_serial.is_connected:
        await async_serial.aio_instance.write_async(text_data.encode())

  async def disconnect(self, close_code):
    print(f'Receive command websocket disconnected {close_code}')


class ConnectionConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()
    #async_serial.initiate_loggers()
    if async_serial != None:
      await async_serial.start_serial_connection(self)

  async def disconnect(self, close_code):
    print(f'Connection websocket disconnected {close_code}')


class PostConsumer(AsyncWebsocketConsumer):
  def __init__(self) -> None:
      super().__init__()
      self.logger_except = None
      self.logger_info = None

  async def connect(self):
    global post_consumer_instance
    await self.accept()
    self.initiate_loggers()
    post_consumer_instance = self

  async def send_via_post(self, text_data):
    config = configparser.ConfigParser()
    config.read('config.ini')
    received_json = json.loads(text_data)

    if received_json.get('ip') is not None:
      ip = str(received_json['ip'])
    else:
      ip = config['post']['ip']

    base_path = config['post']['base_path']
    device_id = str(received_json['receiver'])
    command_code = str(received_json['type'])

    # Device com ID = 0 é o comando "Send to all"
    #if device_id == "0":
    #  async with aiohttp.ClientSession() as session:
        #Paralel for, testar multi thread pool.
    #    for path in paths:
    #      ip = base_ip + path

    #      async with session.post(ip, data=json.loads(text_data)) as resp:
    #        response = await resp.json()
            #await asyncio.sleep(0.1)
            #print(f'ACK: {response}')
    
    url = ip + base_path + device_id + '/' + command_code + '/'
  
    async with aiohttp.ClientSession() as session:
      async with session.post(url, data=received_json) as resp:
        response = await resp.json() 
        #print(f'ACK: {response}')

  async def receive(self, text_data):
    #print(f'Recebeu em consumer:{text_data}')
    if self.logger_info != None:
      self.logger_info.info(text_data)
    
    await self.send_via_post(text_data)

  async def receive_post(self, data):
    data['method'] = 'post'
    data['time'] = get_time().replace('"', '')
    data['status'] = 'active'

    append_json_to_list(data, json_list_persistent)

    if self.logger_info != None:
      self.logger_info.info(data)
    try:
      await self.send(json.dumps(data))
    except Exception:
      if self.logger_except != None:
        self.logger_except.exception('')

  async def disconnect(self, close_code):
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


class UpdatePeriodcallyConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()
    await self.main()

  async def disconnect(self, close_code):
    print(f'Update periodically websocket disconnected {close_code}')

  async def send_json_list(self):
    config = configparser.ConfigParser()
    config.read('config.ini')

    date_format = "%Y-%m-%dT%H:%M:%S.%f"

    while True:
      time_now = datetime.now()
      seconds_to_be_inactive = int(config['consumers']['seconds_to_device_be_inactive'])
      seconds_to_be_on_hold = int(config['consumers']['seconds_to_device_be_on_hold'])

      for json_update in json_list_persistent:
        time_shifted_inactive = datetime.strptime(json_update['time'], date_format) + timedelta(seconds = seconds_to_be_inactive)
        time_shifted_on_hold = datetime.strptime(json_update['time'], date_format) + timedelta(seconds = seconds_to_be_on_hold)
        json_update['status'] = insert_activity_flag(time_now, time_shifted_inactive, time_shifted_on_hold)
        await self.send(json.dumps(json_update))
        await asyncio.sleep(0.1)
      await asyncio.sleep(UPDATE_DELAY)

  async def handle_disconnection_exception(self, tasks):
    for task in tasks:
      task.cancel()

  async def main(self):
    tasks = []
    send_persistent_list = asyncio.create_task(self.send_json_list())

    tasks.extend([send_persistent_list])
    await asyncio.gather(*tasks)
    await self.handle_disconnection_exception(tasks) 


# Auxiliary functions
# -------------------
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


def insert_activity_flag(time_now, time_to_inactive, time_to_on_hold):
  if time_now >= time_to_inactive:
    return 'inactive'
  if time_now >= time_to_on_hold:
    return 'on_hold'
  return 'active' 
  

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


json_list_persistent = []
UPDATE_DELAY = 20

config = configparser.ConfigParser()
config.read('config.ini')

serial_available = config['serial_esp']['serial_available']

async_serial = None
if serial_available != "false":
  async_serial = SerialConnection()

post_consumer_instance = None
