import requests
import config.conf as conf

class MessageHelper:

    @staticmethod
    async def send_group_message(channel_id, content):
        url = f"http://{conf.satori}/v1/message.create"
        payload = {'channel_id': channel_id, 'content': content}
        headers = conf.headers
        requests.post(url, json=payload, headers=headers)

    @staticmethod
    async def send_private_message(channel_id, content):
        url = f"http://{conf.satori}/v1/message.create"
        payload = {
        'channel_id': f'private:{channel_id}',
        'content': content
        }
        headers = conf.headers
        requests.post(url, json=payload, headers=headers)

    @staticmethod
    def format_hoshino_message(message):
        segments = message["params"]["message"]
        formatted_message = ""

        for segment in segments:
            if segment["type"] == "text":
                formatted_message += segment["data"]["text"]

        return formatted_message

    @staticmethod
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
    
    @staticmethod
    def convert_to_onebot_group_format(received_message):
        message_type = "group"
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