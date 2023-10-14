import asyncio
import websockets
import json
import requests
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

async def receive_messages(websocket):
    while True:
        try:
            while True:
                message = await websocket.recv()
                print(message)
                message = json.loads(message)
                if message["op"] == 0:
                    if message['body']['channel']['type'] == 3:
                        onebot_message = convert_to_onebot_format(message)
                    else:
                        onebot_message = convert_to_onebot_group_format(message)
                    
                    headers = {
                        "Upgrade": "websocket",
                        "X-Client-Role": "Universal",
                        "X-Self-ID": "3189539243"
                    } 
                        # 发送消息 
                    async with websockets.connect('ws://192.168.1.3:10024/ws/',extra_headers=headers) as forward_websocket:
                        await forward_websocket.send(json.dumps(onebot_message))
        except Exception as e:
            print(f'Connection to 10024 closed, retrying: {str(e)}')
            await asyncio.sleep(5)  # wait for 5 seconds before retrying

async def send_message(channel_id, content):
    url = 'http://127.0.0.1:5501/v1/message.create'
    payload = {'channel_id': channel_id, 'content': content}
    headers = {'Authorization': 'Bearer 49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136'}
    requests.post(url, json=payload, headers=headers)

async def satori_communication():
    uri = "ws://127.0.0.1:5501/v1/events"
    async with websockets.connect(uri) as websocket: 
        identify_signal = {"op": 3, "body": {"token": "49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136", "sequence": 0}}
        await websocket.send(json.dumps(identify_signal))

        # Create tasks for heartbeat, receiving messages and sending a message
        heartbeat_task = asyncio.create_task(heartbeat(websocket))
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_personal_message('574866115', 'Test Message'))

        await asyncio.gather(heartbeat_task, receive_task, send_task)

asyncio.run(satori_communication())
