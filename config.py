import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    TEXT = os.environ.get('TEXT') or "I'm bot"
    TIMER = int(os.environ.get('TIMER') or 30)
