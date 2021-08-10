from app.exchanges import create_exchange_list, StormGain, Exchange, DealOpeningMethod, ByBit
from app.symbols import Symbol
from app.workers.decition_maker import Side, Decision
from app.workers.rsi_checker import IndicatorInfoRSI


class TestExchange(Exchange):

    @property
    def name(self):
        return 'TestExchange'

    @property
    def deal_opening_method(self):
        return 'TEST'


class SymbolFabric:
    exchange_list = ['stormgain','bybit']
    base_currency = 'BTC'
    quote_currency = 'USDT'

    @classmethod
    def create(
            cls,
            exchange_list=None,
            base_currency=None,
            quote_currency=None,
    ):
        return Symbol(
            exchanges=create_exchange_list(exchange_list or cls.exchange_list),
            base_currency=base_currency or cls.base_currency,
            quote_currency=quote_currency or cls.quote_currency,
        )

    @classmethod
    def create_with_test_exchange(
            cls,
            base_currency=None,
            quote_currency=None,
    ):
        return Symbol(
            exchanges=[TestExchange()],
            base_currency=base_currency or cls.base_currency,
            quote_currency=quote_currency or cls.quote_currency,
        )


class IndicatorInfoRSIFabric:
    symbol = SymbolFabric.create()
    present_value = 32
    previous_value = 68

    @classmethod
    def create(
            cls,
            symbol=None,
            present_value=None,
            previous_value=None,
    ):
        return IndicatorInfoRSI(
            symbol=symbol or cls.symbol,
            present_value=present_value or cls.present_value,
            previous_value=previous_value or cls.previous_value,
        )


class DecisionFabric:
    symbol = SymbolFabric.create()
    side = Side.Buy
    cause = str(IndicatorInfoRSIFabric.create())

    @classmethod
    def create(
            cls,
            symbol=None,
            side=None,
            cause=None,
    ):
        return Decision(
            symbol=symbol or cls.symbol,
            side=side or cls.side,
            cause=cause or cls.cause
        )
