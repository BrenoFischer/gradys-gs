import json
import asyncio
import aioserial
from random import randint

from channels.generic.websocket import AsyncWebsocketConsumer

class ReceiveCommandConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

  async def receive(self, text_data):
    await serial.aio_instance.write_async(text_data.encode())

  async def disconnect(self, close_code):
    print(f'Receive command websocket disconnected {close_code}')


class ConnectionConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

    serial.is_connected = serial.connect_serial()
    while True:
      if serial.is_connected:
        try:
          reader = asyncio.create_task(serial.read())
          consumer = asyncio.create_task(serial.consume(self))
          serial.queue = asyncio.Queue()
          serial.tasks.extend([reader, consumer])
          await asyncio.gather(reader)
          await serial.handle_disconnection_exception()
          serial.is_connected = False
        except Exception as e:
          print(e)
          await serial.handle_disconnection_exception()
          await serial.keep_trying_connection()
      else:
        await serial.keep_trying_connection()

  async def disconnect(self, close_code):
    print(f'Connection websocket disconnected {close_code}')
  

class SerialConnection():
  def __init__(self):
    self.aio_instance = None
    self.is_connected = False
    self.tasks = []
    self.queue = None


  async def handle_disconnection_exception(self):
    await self.queue.join()
    for task in self.tasks:
        task.cancel()


  async def keep_trying_connection(self):
    self.is_connected = False
    while not self.is_connected:
        self.is_connected = self.connect_serial()
        await asyncio.sleep(3)


  async def read(self):
    while True:
      raw_data: bytes = await self.aio_instance.readline_async()
      decoded_line = raw_data.decode('ascii')
      try:
        json_line = json.loads(decoded_line)
        await self.queue.put(json_line)
      except ValueError as e:
        print(e)
        print(decoded_line)


  async def consume(self, obj):
    while True:
      json_consumed = await self.queue.get()
      self.queue.task_done()
      print(f'consumed {json_consumed}')
      await obj.send(json.dumps(json_consumed))


  def connect_serial(self):
    print("Tentando conexão com a serial...")
    try:
      self.aio_instance = aioserial.AioSerial(port='COM4', baudrate=115200)
      self.aio_instance.flush()
      print("Conexão estabelecida")
      return True
    except Exception as e:
      print("Não foi possível conectar")
      print(e)
      return False


serial = SerialConnection()