from trading_bot import app
from trading_bot.adapters.ta_api import AdapterTaAPI
from trading_bot.models.exchanges import ExchangeManager
from trading_bot.models.indicator_values import IndicatorValueManager
from trading_bot.models.indicators import IndicatorManager
from trading_bot.models.symbols import SymbolManager
from trading_bot.models.trading_systems import TradingSystemManager
from trading_bot.services.deal_opener import DealOpener
from trading_bot.services.decision_maker import DecisionMaker
from trading_bot.services.decision_router import DecisionRouter
from trading_bot.services.indicator_updater import IndicatorUpdater
from trading_bot.services.notifier import Notifier
from config import Config


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
    app.indicator_manager = IndicatorManager()
    app.indicator_value_manager = IndicatorValueManager()
    app.exchange_manager = ExchangeManager()
    app.symbol_manager = SymbolManager()
    app.trading_system_manager = TradingSystemManager(app.indicator_manager, app.exchange_manager)

    create_exchanges(app.exchange_manager, config_class.EXCHANGES)
    create_symbols(app.symbol_manager, app.exchange_manager, config_class.SYMBOLS)
    create_trading_systems(app.trading_system_manager, config_class.TRADING_SYSTEMS_SETTINGS)

    app.notifier = Notifier(
        token=config_class.TELEGRAM_TOKEN,
        chat_id=config_class.TELEGRAM_CHAT_ID,
    )
    app.deal_opener = DealOpener()
    app.decision_router = DecisionRouter(app.notifier, app.deal_opener)
    app.decision_maker = DecisionMaker(
        app.trading_system_manager,
        app.symbol_manager,
        app.indicator_value_manager,
        app.decision_router
    )
    app.indicators_adapter = AdapterTaAPI(
        api_key=config_class.TA_API_KEY,
        timeout=config_class.TA_API_TIMEOUT
    )
    app.indicator_updater = IndicatorUpdater(
        indicators_adapter=app.indicators_adapter,
        decision_maker=app.decision_maker,
    )

    return app
