import json
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class SettingsLoader:

    @staticmethod
    def load():
        with open(f'{basedir}/settings.json') as f:
            return json.load(f)


class Config:
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    TA_API_KEY = os.environ.get('TA_API_KEY')
    TA_API_TIMEOUT = int(os.environ.get('TA_API_TIMEOUT') or 15)

    _settings = SettingsLoader.load()

    SYMBOLS = _settings.get('symbols')
    EXCHANGES = _settings.get('exchanges')
    TRADING_SYSTEMS_SETTINGS = _settings.get('trading_system_settings')
