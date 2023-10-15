import os
import logging


# ========================================
# ws setting
# ========================================
satori="127.0.0.1:5501"
token = "49e4a9e837d5f67ad26364d90d88e26d71155460b3c84e40ec9376448d21b136"
#bot地址，可以有多个，会给每个bot转发
ws_servers = [
    "ws://192.168.1.3:10024/ws",
    ]
# ========================================
# message setting
# ========================================
identify_signal = {
            "op": 3,
            "body": {
                "token": token,
                "sequence": 0
            }
        }

headers = {'Authorization': f'Bearer {token}'}
# ========================================
# Log setting
# ========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE_NAME = "adapter.log"
LOG_FILE_PATH = os.path.join(BASE_DIR, LOG_FILE_NAME)
# Switch to output log to file
LOG_TO_FILE = True  # False
# Switch to output log to console
LOG_TO_CONSOLE = True
# Level of output log
# FATAL / ERROR / WARN / INFO / DEBUG
LOG_LEVEL = logging.INFO
