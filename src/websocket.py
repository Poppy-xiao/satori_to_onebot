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
        self.connections = {ws: {} for ws in conf.ws_servers}
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


    async def forward_receive_messages(self, ws_server, self_id):
        if self_id in self.connections[ws_server]:
            websocket = self.connections[ws_server][self_id]
            while True:
                try:
                    message = await websocket.recv()
                    self.logger.info(message)
                    message = json.loads(message)
                    await self.queue_hoshino.put((ws_server, message))  # 保存ws_server信息
                except Exception:
                    msg = traceback.format_exc()
                    self.logger.error(f"[forward_receive_messages]{msg}")
                    await asyncio.sleep(5)  # wait before retrying

    async def process_queue_satori_and_send(self):
        while True:
            try:
                message = await self.queue_satori.get()
                self.logger.info(message)
                # 使用 EventProcessor 处理消息
                formatted_message = await EventProcessor().process(message)
                # 如果消息有效，发送到bot
                if formatted_message:
                    self_id = message['body']['self_id']
                    await self.send_to_all_bot(self_id, formatted_message) 
            except:
                msg = traceback.format_exc()
                self.logger.error(f"[process_queue_satori_and_send]{msg}")


    async def process_queue_hoshino_and_send(self, websocket):
        while True:
            try:
                ws_server, message = await self.queue_hoshino.get()
                formatted_message = MessageHelper.format_hoshino_message(message)
                # 发送到 satori
                channel_id = message["params"]["group_id"]
                #TODO
                # 处理bot消息事件未完成
                await MessageHelper.send_group_message(channel_id, formatted_message)
            except:
                msg = traceback.format_exc()
                self.logger.error(f"[process_queue_hoshino_and_send]{msg}")


    async def send_to_all_bot(self, self_id, onebot_message):
        for ws_server in conf.ws_servers:
            await self.send_to_bot(ws_server, self_id, onebot_message)

    async def send_to_bot(self, ws_server, self_id, onebot_message):
        if self_id not in self.connections[ws_server] or self.connections[ws_server][self_id].closed:
            headers = {
                "Upgrade": "websocket",
                "X-Client-Role": "Universal",
                "X-Self-ID": str(self_id)
            }
            forward_websocket = await websockets.connect(ws_server, extra_headers=headers)
            self.connections[ws_server][self_id] = forward_websocket
            asyncio.create_task(self.forward_receive_messages(ws_server, self_id))

        try:
            await self.connections[ws_server][self_id].send(json.dumps(onebot_message))
        except:
            msg = traceback.format_exc()
            self.logger.error(f"[send_to_bot]{msg}")

