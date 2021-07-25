from app.main import Printer
from config import Config


def create_app(config_class=Config):
    return Printer(config_class.TEXT)
