import logging

from trading_bot import app
from trading_bot.adapters.by_bit import AdapterByBit
from trading_bot.adapters.ta_api import AdapterTaAPI
from trading_bot.models.exchanges import ExchangeManager
from trading_bot.models.indicator_values import IndicatorValueManager
from trading_bot.models.indicators import IndicatorManager
from trading_bot.models.symbols import SymbolManager
from trading_bot.models.trading_systems import TradingSystemManager
from trading_bot.services.dealer import Dealer
from trading_bot.services.decision_maker import DecisionMaker
from trading_bot.services.indicator_updater import IndicatorUpdater
from trading_bot.services.stop_loss_manager import StopLossManager
from trading_bot.adapters.telegram import AdapterTelegram
from config import Config
from trading_bot.services.pause_checker import PauseChecker


def create_exchanges(exchange_manager, exchanges_config):
    for exchange in exchanges_config:
        exchange_manager.create(
            name=exchange['name'],
            deal_opening_method=exchange['deal_opening_method']
        )


def create_symbols(symbol_manager, exchange_manager, symbols_config):
    for symbol in symbols_config:
        exchanges = []
        for ex in symbol['exchanges']:
            exchanges.append(exchange_manager.get(ex))

        symbol_manager.create(
            base_currency=symbol['base_currency'],
            quote_currency=symbol['quote_currency'],
            exchanges=exchanges,
            deal_opening_params=symbol['deal_opening_params'],
        )


def create_trading_systems(trading_system_manager, trading_systems_config):
    for tr_system in trading_systems_config:
        trading_system_manager.create(
            name=tr_system['name'],
            settings=tr_system['settings']
        )


def create_app(config_class=Config):
    logger = logging.getLogger('logger')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] [%(module)s] %(message)s'))
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)
    logger.info("I'm up and running")

    app.indicator_manager = IndicatorManager()
    app.indicator_value_manager = IndicatorValueManager()
    app.exchange_manager = ExchangeManager()
    app.symbol_manager = SymbolManager()
    app.trading_system_manager = TradingSystemManager(app.indicator_manager, app.exchange_manager)

    create_exchanges(app.exchange_manager, config_class.EXCHANGES)
    create_symbols(app.symbol_manager, app.exchange_manager, config_class.SYMBOLS)
    create_trading_systems(app.trading_system_manager, config_class.TRADING_SYSTEMS_SETTINGS)

    app.notifier = AdapterTelegram(
        token=config_class.TELEGRAM_TOKEN,
        chat_id=config_class.TELEGRAM_CHAT_ID,
    )
    app.deals_adapter = AdapterByBit(
        api_key=config_class.BY_BIT_API_KEY,
        api_secret=config_class.BY_BIT_API_SECRET,
    )
    app.dealer = Dealer(deals_adapter=app.deals_adapter)

    app.decision_maker = DecisionMaker(
        app.trading_system_manager,
        app.symbol_manager,
        app.indicator_value_manager,
    )
    app.indicators_adapter = AdapterTaAPI(
        api_key=config_class.TA_API_KEY,
        timeout=config_class.TA_API_TIMEOUT
    )
    app.indicator_updater = IndicatorUpdater(
        indicator_adapter=app.indicators_adapter,
        decision_maker=app.decision_maker,
    )

    app.pause_checker = PauseChecker(
        dealer=app.dealer
    )

    app.stop_loss_manager = StopLossManager(
        indicator_value_manager=app.indicator_value_manager
    )

    return app
