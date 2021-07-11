import json
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
    print(data)
    self.send(json.dumps(data))

  def disconnect(self, close_code):
    print(f'Post websocket disconnected {close_code}')


def get_post_consumer_instance():
  global post_consumer_instance
  return post_consumer_instance


async_serial = SerialConnection()
post_consumer_instance = None
