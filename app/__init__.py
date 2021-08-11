from app.app import App
from app.workers.deal_opening_router import DealOpeningRouter
from app.workers.rsi_checker import IndicatorCheckerRSI
from app.workers.notifier import Notifier
from app.workers.decition_maker import DecisionMaker
from app.symbols import create_symbol_list
from config import Config


def create_app(config_class=Config):

    symbols = create_symbol_list(
        config_class.STORMGAIN_SYMBOLS,
        config_class.BYBIT_SYMBOLS,
    )

    rsi_checker = IndicatorCheckerRSI(
        symbols=symbols,
        ta_api_key=config_class.TA_API_KEY,
        timeout=config_class.TA_API_TIMEOUT,
    )

    notifier = Notifier(
        token=config_class.TELEGRAM_TOKEN,
        chat_id=config_class.TELEGRAM_CHAT_ID,
    )

    app = App(
        rsi_checker=rsi_checker,
        decision_maker=DecisionMaker(),
        deal_opening_router=DealOpeningRouter(),
        notifier=notifier
    )

    return app
