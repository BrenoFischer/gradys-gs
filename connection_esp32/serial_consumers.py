import configparser
from .serial_connector import SerialConnection
from channels.generic.websocket import AsyncWebsocketConsumer


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


config = configparser.ConfigParser()
config.read('config.ini')
serial_available = config['serial_esp']['serial_available']

async_serial = None
if serial_available != "false":
  async_serial = SerialConnection()