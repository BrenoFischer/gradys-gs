import json
import asyncio
import aioserial
import logging
import serial
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer

class ReceiveCommandConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

  async def receive(self, text_data):
    await async_serial.aio_instance.write_async(text_data.encode())

  async def disconnect(self, close_code):
    print(f'Receive command websocket disconnected {close_code}')


class ConnectionConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

    time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = "./connection_esp32/LOGS/"

    log_file_name_exc = path + f'exceptions/{time_now}.log'
    async_serial.logger_except = async_serial.setup_logger('log_exception', log_file_name_exc, '%(lineno)d: %(asctime)s %(message)s', level=logging.ERROR)

    log_file_name_info = path + f'info/{time_now}.log'
    async_serial.logger_info = async_serial.setup_logger('log_info', log_file_name_info, '%(asctime)s %(message)s', level=logging.INFO)

    async_serial.is_connected = async_serial.connect_serial()
    while True:
      if async_serial.is_connected:
        try:
          await async_serial.set_tasks(self)
          await async_serial.handle_disconnection_exception()
          async_serial.is_connected = False
        except Exception as e:
          print(e)
          await async_serial.handle_disconnection_exception()
          await async_serial.keep_trying_connection()
      else:
        await async_serial.keep_trying_connection()

  async def disconnect(self, close_code):
    print(f'Connection websocket disconnected {close_code}')
  

class SerialConnection():
  def __init__(self):
    self.aio_instance = None
    self.is_connected = False
    self.tasks = []
    self.queue = None
    self.logger_info = None
    self.logger_except = None


  def setup_logger(self, name, log_file, my_format, level=logging.INFO):
    formatter = logging.Formatter(my_format)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    lo = logging.getLogger(name)
    lo.setLevel(level)
    lo.addHandler(handler)

    return lo

  async def set_tasks(self, obj):
    reader = asyncio.create_task(self.read())
    consumer = asyncio.create_task(self.consume(obj))
    self.queue = asyncio.Queue()
    self.tasks.extend([reader, consumer])
    await asyncio.gather(reader)


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
      except ValueError:
        self.logger_except.exception('')


  async def consume(self, obj):
    while True:
      json_consumed = await self.queue.get()
      self.queue.task_done()
      print(f'consumed {json_consumed}')
      self.logger_info.info(json_consumed)
      await obj.send(json.dumps(json_consumed))


  def connect_serial(self):
    print("Tentando conexão com a serial...")
    try:
      self.aio_instance = aioserial.AioSerial(port='COM4', baudrate=115200)
      self.aio_instance.flush()
      print("Conexão estabelecida")
      return True
    except serial.serialutil.SerialException:
      self.logger_except.exception('')
      return False


async_serial = SerialConnection()