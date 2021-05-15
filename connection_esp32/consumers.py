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
    if async_serial.is_connected:
      await async_serial.aio_instance.write_async(text_data.encode())

  async def disconnect(self, close_code):
    print(f'Receive command websocket disconnected {close_code}')


class ConnectionConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()
    async_serial.initiate_loggers()
    await async_serial.start_serial_connection(self)

  async def disconnect(self, close_code):
    print(f'Connection websocket disconnected {close_code}')


class SerialConnection():
  """
  Attributes
  ----------
  aio_instance : AioSerial
    will handle the connection, send and receive async messages

  is_connected : bool
    control the serial connection status

  tasks : List(Task)
    async methods that'll act as tasks gathered with the asyncio library

  queue : Queue
    queue of messages received from the serial
  
  logger_info : Logger
    logger that'll control and generate the information log file

  logger_except : Logger
    logger that'll control and generate the exception log file


  Methods
  ---------
  setup_logger(name, log_file, my_format, level=logging.INFO)
    Return the logger, according to it's logging purpose.

  set_tasks(obj)
    Create the reader, consumer tasks, the queue and keep waiting them to finish

  handle_disconnection_exception()
    Put the connection status to false, wait for the queue to be cleared and cancel the tasks

  keep_trying_connection()
    While the serial connection is not established, keep trying connection

  read()
    Keep waiting for messages from the serial and put it in the queue

  consume(obj)
    Keep waiting for a message in the queue, put the info in the log file and send it to the client,
    through websocket

  connect_serial()
    Try to instantiate the aioserial connector and change the serial status accordingly
  """

  def __init__(self):
    self.aio_instance = None
    self.is_connected = False
    self.tasks = []
    self.queue = None
    self.logger_info = None
    self.logger_except = None
    self.handshake_json =  {"id": "3", "type": 13, "seq": 0, "ACK": 0, "SDATA": 0, "lat": -9, "lng": 10, "high": 11}
    self.connected_json = {"id": "3", "type": 14, "seq": 0, "ACK": 0, "SDATA": 0, "lat": -9, "lng": 10, "high": 11}

  def setup_logger(self, name, log_file, my_format, level=logging.INFO):
    """
    Parameters
    ----------
    name : str
      name that indicates which logger is
    log_file : str
      path and name of the log file
    my_format : str
      format of the information put inside of the log file
    level : INFO, optional
      hierarchical level of information interest to catch (DEBUG, INFO, WARNING, ERROR, CRITICAL)
      (default is INFO)

    Returns
    ----------
    LOGGER
      a setted up logger 
    """
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

    log_file_name_exc = path + f'exceptions/{time_now}.log'
    self.logger_except = self.setup_logger('log_exception', log_file_name_exc, '%(lineno)d: %(asctime)s %(message)s', level=logging.ERROR)

    log_file_name_info = path + f'info/{time_now}.log'
    self.logger_info = self.setup_logger('log_info', log_file_name_info, '%(asctime)s %(message)s', level=logging.INFO)


  async def set_tasks(self, obj):
    reader = asyncio.create_task(self.read())
    consumer = asyncio.create_task(self.consume(obj))
    self.queue = asyncio.Queue()
    self.tasks.extend([reader, consumer])
    await asyncio.gather(reader)


  async def handle_disconnection_exception(self):
    self.is_connected = False
    await self.queue.join()
    for task in self.tasks:
        task.cancel()


  async def keep_trying_connection(self, obj):
    while not self.is_connected:
        await self.connect_serial(obj)
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


  async def connect_serial(self, obj):
    print("Tentando conexão com a serial...")
    try:
      self.aio_instance = aioserial.AioSerial(port='COM4', baudrate=115200)
      self.aio_instance.flush()
      print("Conexão estabelecida")
      self.is_connected = True
      await obj.send(json.dumps(self.connected_json))
    except serial.serialutil.SerialException:
      self.logger_except.exception('')
      self.is_connected = False
      await obj.send(json.dumps(self.handshake_json))


  async def start_serial_connection(self, obj):
    await obj.send(json.dumps(self.handshake_json))
    await self.connect_serial(obj)
    while True:
      if self.is_connected:
        await obj.send(json.dumps(self.connected_json))
        try:
          await self.set_tasks(obj)
        except Exception:
          await self.handle_disconnection_exception()
          await obj.send(json.dumps(self.handshake_json))
          await self.keep_trying_connection(obj)
      else:
        await self.keep_trying_connection(obj)


async_serial = SerialConnection()