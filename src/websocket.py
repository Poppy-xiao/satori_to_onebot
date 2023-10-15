import asyncio
import websockets
import json
import traceback
from src.event import EventProcessor
from src.message import MessageHelper
import config.conf as conf
from src.logger import get_logger
class WebSocketServer:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.connections = {}
        self.queue_satori = asyncio.Queue(loop=self.loop)
        self.queue_hoshino = asyncio.Queue(loop=self.loop)
        self.logger = get_logger()

    def run(self):
        self.loop.run_until_complete(self.satori_communication())

    async def heartbeat(self,websocket):
        while True:
            try:
                await asyncio.sleep(10)
                await websocket.send(json.dumps({"op": 1}))
            except Exception:
                msg = traceback.format_exc()
                self.logger.error(f"[heartbeat] Error sending heartbeat{msg}")
                await asyncio.sleep(5)

    async def receive_messages(self, websocket):
        while True:
            try:
                message = await websocket.recv()
                message = json.loads(message)
                if message["op"] == 0:
                    await self.queue_satori.put(message)  # 放入队列
            except Exception:
                msg = traceback.format_exc()
                self.logger.error(f"[receive_messages] {msg}")
                await asyncio.sleep(5)
                
    async def satori_communication(self):
        async with websockets.connect(f"ws://{conf.satori}/v1/events") as websocket:
            await websocket.send(json.dumps(conf.identify_signal))
            heartbeat_task = asyncio.create_task(self.heartbeat(websocket))
            receive_messages_task = asyncio.create_task(self.receive_messages(websocket))
            process_satori_task = asyncio.create_task(self.process_queue_satori_and_send())
            process_hoshino_task = asyncio.create_task(self.process_queue_hoshino_and_send(websocket))

            await asyncio.gather(heartbeat_task, receive_messages_task, process_satori_task, process_hoshino_task)


    async def forward_receive_messages(self, self_id):
        if self_id in self.connections:
            websocket = self.connections[self_id]
            message = None
            while True:
                try:
                    message = await websocket.recv()
                    message = json.loads(message)
                    await self.queue_hoshino.put(message)  # 放入队列
                except Exception as e:
                    print(f'Error {traceback.format_exc()}')
                    await asyncio.sleep(5)  # wait before retrying

    async def process_queue_satori_and_send(self):
        while True:
            try:
                message = await self.queue_satori.get()
                # 使用 EventProcessor 处理消息
                formatted_message = await EventProcessor().process(message)
                # 如果消息有效，发送到 hoshino
                if formatted_message:
                    self_id = message['body']['self_id']
                    await self.send_to_hoshino(self_id, formatted_message) 
            except:
                msg = traceback.format_exc()
                self.logger.error(f"[send_to_hoshino]{msg}")


    async def process_queue_hoshino_and_send(self, websocket):
        while True:
            try:
                message = await self.queue_hoshino.get()
                formatted_message = MessageHelper.format_hoshino_message(message)
                # 发送到 satori
                channel_id = message["params"]["group_id"]
                #TODO
                # 处理星乃消息事件未完成
                await MessageHelper.send_group_message(channel_id, formatted_message)
            except:
                msg = traceback.format_exc()
                self.logger.error(f"[send_to_hoshino]{msg}")


    async def send_to_hoshino(self, self_id, onebot_message):
        if self_id not in self.connections or self.connections[self_id].closed:
            uri = f"ws://{conf.hoshino}/ws/"
            headers = {
                "Upgrade": "websocket",
                "X-Client-Role": "Universal",
                "X-Self-ID": str(self_id)
            }
            forward_websocket = await websockets.connect(uri, extra_headers=headers)
            self.connections[self_id] = forward_websocket
            # 启动一个新的任务来接收Hoshino的消息
            asyncio.create_task(self.forward_receive_messages(self_id))

        try:
            await self.connections[self_id].send(json.dumps(onebot_message))
        except:
            msg = traceback.format_exc()
            self.logger.error(f"[send_to_hoshino]{msg}")

