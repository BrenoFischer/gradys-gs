import configparser
import json
import asyncio
from datetime import datetime, timedelta

from channels.generic.websocket import AsyncWebsocketConsumer


class UpdatePeriodcallyConsumer(AsyncWebsocketConsumer):
  # Websocket consumer that is in charge to store, manipulate and send periodically the persistent list of devices that sent info.
  # The interval of time that the list will be sent to JS via socket, is set in the config.ini file.
  def __init__(self) -> None:
    super().__init__()
    self.tasks = []


  async def connect(self):
    # When the socket connection is stablished, it'll run the looping task to send the list, called in the 'main()'.
    await self.accept()
    await self.main()


  async def disconnect(self, close_code):
    await self.handle_disconnection_exception()
    print(f'Update periodically websocket disconnected {close_code}')


  async def handle_disconnection_exception(self):
    for task in self.tasks:
      task.cancel()


  async def send_device_list(self):
    # The task will send to JS every UPDATE_DELAY seconds the persistent list of devices info received.
    # Also it'll change the activity status of the devices on the list based on:
    # Time now; Time when the msg arrived; Amount of seconds to be considered 'inactive' and 'on hold'. 
    date_format = "%Y-%m-%dT%H:%M:%S.%f"

    while True:
      time_now = datetime.now()
      seconds_to_be_inactive = int(config['list-updater']['seconds_to_device_be_inactive'])
      seconds_to_be_on_hold = int(config['list-updater']['seconds_to_device_be_on_hold'])

      for device_update in device_list_persistent:
        time_shifted_inactive = datetime.strptime(device_update['time'], date_format) + timedelta(seconds = seconds_to_be_inactive)
        time_shifted_on_hold = datetime.strptime(device_update['time'], date_format) + timedelta(seconds = seconds_to_be_on_hold)
        device_update['status'] = insert_activity_flag(time_now, time_shifted_inactive, time_shifted_on_hold)
        await self.send(json.dumps(device_update))
        await asyncio.sleep(0.1)
      await asyncio.sleep(UPDATE_DELAY)


  async def main(self):
    # It'll create the looping task and wait for it to finish (only finishable when connection is closed)
    send_persistent_list = asyncio.create_task(self.send_device_list())

    self.tasks.extend([send_persistent_list])
    await asyncio.gather(*self.tasks)
    await self.handle_disconnection_exception()


# --- Auxiliary functions ---
def insert_activity_flag(time_now, time_to_inactive, time_to_on_hold):
  # The flag will be base on:
  # Time now >= time msg arrived + amount of time to be considered inactive?
  # Time now >= time msg arrived + amount of time to be considered on hold?
  if time_now >= time_to_inactive:
    return 'inactive'
  if time_now >= time_to_on_hold:
    return 'on_hold'
  return 'active' 


def get_device_from_list_by_id(id):
  # Return list of single json of the device with the id received as param.
  # If the id is 'all' return the whole list.
  # Return empty list if not found.
  if id == 'all':
    return device_list_persistent

  for device in device_list_persistent:
    if str(device['id']) == id:
      return [device]
  return []


def append_device_to_persistant_list(data):
  # Receive a device info, checks if the device is already on list and if it's more recent.
  # Append the new info and remove the old one, if it's the case.
  device_already_on_array_index = -1
  for i,device in enumerate(device_list_persistent):
    if device['id'] == data['id']:
      if device['time'] < data['time']:
        device_already_on_array_index = i
      break

  if device_already_on_array_index != -1:
    device_list_persistent.pop(device_already_on_array_index)
  device_list_persistent.append(data)
# --- End of Auxiliary functions ---


# --- Reading the delay to send the info to JS ---
config = configparser.ConfigParser()
config.read('config.ini')
UPDATE_DELAY = float(config['list_updater']['update_delay'])
# --- End of read ---

device_list_persistent = []