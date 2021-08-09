import json
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    TA_API_KEY = os.environ.get('TA_API_KEY')
    STORMGAIN_SYMBOLS = json.loads(os.environ.get('STORMGAIN_SYMBOLS'))
    BYBIT_SYMBOLS = json.loads(os.environ.get('BYBIT_SYMBOLS'))
    TA_API_TIMEOUT = int(os.environ.get('TA_API_TIMEOUT') or 15)
