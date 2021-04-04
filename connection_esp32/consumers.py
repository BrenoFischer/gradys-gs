import json
import asyncio
from random import randint

from channels.generic.websocket import AsyncWebsocketConsumer

class ConnectionConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

    counter = asyncio.create_task(count(self))
    await asyncio.gather(counter)


async def count(obj):
    global i
    while True:
      i+=1
      await obj.send(json.dumps({'value': i}))
      print(i)
      await asyncio.sleep(1)


i = 0
