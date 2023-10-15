import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from config.conf import LOG_TO_FILE, LOG_TO_CONSOLE, LOG_FILE_PATH, LOG_LEVEL

logger = None


def _init_logger(log_file, log_level, maxBytes=5 * 1024 * 1024, backupCount=5):
    dir_name = os.path.dirname(log_file)
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except Exception:
            sys.exit(1)
    logger = logging.getLogger("")
    logger.setLevel(log_level)
    
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")

    if LOG_TO_FILE:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=maxBytes, backupCount=backupCount
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(log_file=LOG_FILE_PATH, log_level=LOG_LEVEL):
    global logger
    if logger is None:
        logger = _init_logger(log_file, log_level)
    return logger


if __name__ == "__main__":
    get_logger().debug("log debug")
    get_logger().info("log info")
    get_logger().warning("log warning")
    get_logger().error("log error")
