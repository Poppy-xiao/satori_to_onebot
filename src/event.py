from config.event import *
from src.message import MessageHelper

class EventProcessor:
    def __init__(self):
        self.configs = MESSAGE
        self.handlers = {}
        for config in self.configs:
            handler_name = config["handler"]
            if hasattr(self, handler_name):
                self.handlers[handler_name] = getattr(self, handler_name)

    async def process(self, message):
        custom_type = self.determine_custom_type(message)
        handler = self.handlers.get(custom_type, None)
        if handler:
            return await handler(message)
        return None

    def determine_custom_type(self, message):
        for config in self.configs:
            if config["matcher"] == message['body']['channel']['type']:
                return config["type"]
        return None

    async def handle_private_message(self, message):
        formatted_message = MessageHelper.convert_to_onebot_format(message)
        return formatted_message

    async def handle_group_message(self, message):
        formatted_message = MessageHelper.convert_to_onebot_group_format(message)
        return formatted_message
