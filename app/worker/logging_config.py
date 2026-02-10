import logging
from pythonjsonlogger import jsonlogger
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
logger.addHandler(handler)
