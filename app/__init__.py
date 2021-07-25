from app.main import App
from config import Config


def create_app(config_class=Config):
    return App(config_class.TEXT, config_class.TIMER)
