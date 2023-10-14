import asyncio
import websockets
import json
import requests
import traceback
connections = {}  # 用于存储每个X-Self-ID的连接

def format_hoshino_message(message):
    segments = message["params"]["message"]
    formatted_message = ""

    for segment in segments:
        if segment["type"] == "text":
            formatted_message += segment["data"]["text"]
        elif segment["type"] == "at":
            formatted_message += f"@{segment['data']['qq']} "

    return formatted_message


def convert_to_onebot_format(message):
    onebot_message = {
        "message_type": "group",
        "user_id": message['body']['user']['id'],
        "message": message['body']['message']['content'],
        "raw_message": message,
        "self_id": message['body']['self_id'],
        "timestamp": message['body']['timestamp'],
        "group_id": message['body']['guild']['id'],
        "sender": {
            "user_id": message['body']['user']['id'],
            "nickname": message['body']['member']['name'],
        }
    }
    return onebot_message


def convert_to_onebot_group_format(received_message):
    message_type = "group"  # 假设是群组消息
    time = received_message["body"]["timestamp"]
    self_id = received_message["body"]["self_id"]
    message_content = received_message["body"]["message"]["content"]
    user_id = received_message["body"]["user"]["id"]
    group_id = received_message["body"]["channel"]["id"]

    # 构建新的消息格式
    new_message = {
        "post_type": "message",
        "message_type": message_type,
        "time": time,
        "self_id": self_id,
        "sub_type": "normal",
        "message_seq": 314708,
        "raw_message": message_content,
        "anonymous": None,
        "message": message_content,
        "sender": {
            "age": 0,
            "area": "",
            "card": user_id,
            "level": "",
            "nickname": "QwQ",
            "role": "member",
            "sex": "unknown",
            "title": "",
            "user_id": user_id
        },
        "user_id": user_id,
        "message_id": -946684545,
        "font": 0,
        "group_id": group_id
    }
    return new_message
async def send_personal_message(channel_id, content):
    url = 'http://127.0.0.1:5501/v1/message.create'
    payload = {
    'channel_id': f'private:{channel_id}',
    'content': content
    }
    headers = {'Authorization': 'Bearer 49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136'}
    requests.post(url, json=payload, headers=headers)

async def send_group_message(channel_id, content):
    url = 'http://127.0.0.1:5501/v1/message.create'
    payload = {'channel_id': channel_id, 'content': content}
    headers = {'Authorization': 'Bearer 49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136'}
    requests.post(url, json=payload, headers=headers)

async def heartbeat(websocket):
    while True:
        try:
            await asyncio.sleep(10)
            await websocket.send(json.dumps({"op": 1}))
        except Exception as e:
            print(f'Connection to 10024 closed, retrying: {str(e)}')
            await asyncio.sleep(5)  # wait for 5 seconds before retrying

async def safe_send_to_forward_ws(self_id, onebot_message):
    uri = "ws://192.168.1.3:10024/ws/"
    headers = {
        "Upgrade": "websocket",
        "X-Client-Role": "Universal",
        "X-Self-ID": str(self_id)
    }

    if self_id not in connections or connections[self_id].closed:
        # 如果连接不存在或已关闭，尝试重新连接
        forward_websocket = await websockets.connect(uri, extra_headers=headers)
        connections[self_id] = forward_websocket
        # 启动一个任务来接收返回的消息
        asyncio.create_task(forward_receive_messages(self_id))
    
    try:
        await connections[self_id].send(json.dumps(onebot_message))
    except:
        # 如果发送失败，尝试重新连接然后再次发送
        forward_websocket = await websockets.connect(uri, extra_headers=headers)
        connections[self_id] = forward_websocket
        await connections[self_id].send(json.dumps(onebot_message))

async def forward_receive_messages(self_id):
    if self_id in connections:
        websocket = connections[self_id]
        message = None
        while True:
            try:
                message = await websocket.recv()
                message = json.loads(message)
                formatted_message = format_hoshino_message(message)
                channel_id = message["params"]["group_id"]
                await send_group_message(channel_id, formatted_message)
                print(message)
            except Exception as e:
                print(message)
                print(f'Error {traceback.format_exc()}')
                await asyncio.sleep(5)  # wait before retrying

async def receive_messages(websocket):
    while True:
        try:
            message = await websocket.recv()
            message = json.loads(message)
            if message["op"] == 0:
                self_id = message['body']['self_id']
                if message['body']['channel']['type'] == 3:
                    onebot_message = convert_to_onebot_format(message)
                else:
                    onebot_message = convert_to_onebot_group_format(message)
                
                # 使用新的安全发送函数
                await safe_send_to_forward_ws(self_id, onebot_message)
        except Exception as e:
            print(f'Error receiving from satori: {str(e)}')
            await asyncio.sleep(5)  # wait before retrying

async def send_message(channel_id, content):
    url = 'http://127.0.0.1:5501/v1/message.create'
    payload = {'channel_id': channel_id, 'content': content}
    headers = {'Authorization': 'Bearer 49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136'}
    requests.post(url, json=payload, headers=headers)

async def satori_communication():
    uri = "ws://127.0.0.1:5501/v1/events"
    async with websockets.connect(uri) as websocket: 
        identify_signal = {
            "op": 3,
            "body": {
                "token": "49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136",
                "sequence": 0
            }
        }
        await websocket.send(json.dumps(identify_signal))

        # Create tasks for heartbeat and receiving messages
        heartbeat_task = asyncio.create_task(heartbeat(websocket))
        receive_task = asyncio.create_task(receive_messages(websocket))

        await asyncio.gather(heartbeat_task, receive_task)


asyncio.run(satori_communication())
