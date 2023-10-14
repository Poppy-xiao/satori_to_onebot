import requests

def send_personal_message(channel_id, content):
    url = 'http://127.0.0.1:5501/v1/message.create'
    payload = {
    'channel_id': f'private:{channel_id}',
    'content': content
    }
    headers = {'Authorization': 'Bearer 49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136'}
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    return None

def send_group_message(channel_id, content):
    url = 'http://127.0.0.1:5501/v1/message.create'
    payload = {'channel_id': channel_id, 'content': content}
    headers = {'Authorization': 'Bearer 49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136'}
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    return None
# 使用方法:

response = send_group_message('1037323224', '测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试')
# 