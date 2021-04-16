import json
import asyncio
import aioserial
from random import randint

from channels.generic.websocket import AsyncWebsocketConsumer

class ReceiveCommandConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

  async def receive(self, text_data):
    await aio_instance.write_async(text_data.encode())
    await self.send(text_data)


class ConnectionConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

    #connect_to_esp()

    if connect_to_esp() == True:
      queue = asyncio.Queue()
      reader = asyncio.create_task(read_json(queue))
      consumer = asyncio.create_task(consume(queue, self))
      await asyncio.gather(reader)


  async def receive(self, text_data):
    await aio_instance.write_async(text_data.encode())
    await self.send(text_data)
  

async def read_json(queue):
  while True:
    raw_data: bytes = await aio_instance.readline_async()
    decoded_line = raw_data.decode('ascii')
    try:
      json_line = json.loads(decoded_line)
      await queue.put(json_line)
    except ValueError as e:
      print(e)
      print(decoded_line)


async def consume(queue, obj):
  while True:
    json_consumed = await queue.get()
    queue.task_done()
    print(f'consumed {json_consumed}')
    await obj.send(json.dumps(json_consumed))


def connect_to_esp():
  print("Tentando conexão com a serial...")
  try:
    global aio_instance
    aio_instance = aioserial.AioSerial(port='COM4', baudrate=115200)
    aio_instance.flush()
    print("Conexão estabelecida")
    return True
  except serial.serialutil.SerialException as e:
    print("Não foi possível conectar")
    print(e)
    return False

aio_instance = None