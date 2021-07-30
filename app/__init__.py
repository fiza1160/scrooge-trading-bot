from app.app import App
from app.rsi_checker import IndicatorCheckerRSI
from app.notifier import Notifier
from app.decition_maker import DecisionMaker
from config import Config


def create_app(config_class=Config):
    rsi_checker = IndicatorCheckerRSI(
        symbols=config_class.STORMGAIN_SYMBOLS,
        ta_api_key=config_class.TA_API_KEY,
        timeout=config_class.TA_API_TIMEOUT,
    )

    notifier = Notifier(
        token=config_class.TELEGRAM_TOKEN,
        chat_id=config_class.TELEGRAM_CHAT_ID,
    )

    app = App(
        notifier=notifier,
        rsi_checker=rsi_checker,
        decision_maker=DecisionMaker()
    )

    return app
