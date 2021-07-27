from app.main import App, Notifier, RsiChecker, DecisionMaker
from config import Config


def create_app(config_class=Config):

    rsi_checker = RsiChecker(
        ta_api_key=config_class.TA_API_KEY,
        coins=config_class.STORMGAIN_COINS,
        timeout=config_class.TA_API_TIMEOUT,
    )

    notifier = Notifier(
        token=config_class.TELEGRAM_TOKEN,
        chat_id = config_class.TELEGRAM_CHAT_ID,
    )

    app = App(
        notifier=notifier,
        rsi_checker=rsi_checker,
        decision_maker=DecisionMaker()
    )

    return app
