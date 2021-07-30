from app.main import App, IndicatorCheckerRSI, Notifier, DecisionMaker
from config import Config


def create_app(config_class=Config):
    rsi_checker = IndicatorCheckerRSI(
        coins=config_class.STORMGAIN_COINS,
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
