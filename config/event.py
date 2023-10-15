#Hoshino和Satori之间的消息转发定义
MESSAGE = [
    #TODO
    #私聊消息处理
    {
        "type": "handle_private_message",
        "matcher": 3,
        "handler": "handle_private_message"
    },
    #群聊消息处理
    {
        "type": "handle_group_message",
        "matcher": 0,
        "handler": "handle_group_message"
    }
]