import configparser
import json
import asyncio
from datetime import datetime, timedelta

from channels.generic.websocket import AsyncWebsocketConsumer


class UpdatePeriodcallyConsumer(AsyncWebsocketConsumer):
  def __init__(self) -> None:
    super().__init__()
    self.tasks = []

  async def connect(self):
    await self.accept()
    await self.main()

  async def disconnect(self, close_code):
    for task in self.tasks:
      task.cancel()
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

  async def handle_disconnection_exception(self):
    for task in self.tasks:
      task.cancel()

  async def main(self):
    send_persistent_list = asyncio.create_task(self.send_json_list())

    self.tasks.extend([send_persistent_list])
    await asyncio.gather(*self.tasks)
    await self.handle_disconnection_exception()


def insert_activity_flag(time_now, time_to_inactive, time_to_on_hold):
  if time_now >= time_to_inactive:
    return 'inactive'
  if time_now >= time_to_on_hold:
    return 'on_hold'
  return 'active' 


def get_device_from_list_by_id(id):
  #Retorna o json do device com id recebido como parêmetro, Retorna None caso não encontre
  if id == 'all':
    return json_list_persistent

  for device in json_list_persistent:
    if str(device['id']) == id:
      return device
  return None


def append_json_to_persistant_list(data):
  drone_already_on_array = False
  for i,drone in enumerate(json_list_persistent):
    if drone['id'] == data['id']:
      drone_already_on_array = True
      if drone['time'] < data['time']:
        json_list_persistent.pop(i)
        json_list_persistent.append(data)
      break

  if not drone_already_on_array:
    json_list_persistent.append(data)


json_list_persistent = []
UPDATE_DELAY = 20