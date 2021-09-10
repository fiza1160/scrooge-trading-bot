from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from trading_bot import AdapterByBit, app
from trading_bot.services.decision_maker import DealSide, DecisionMaker
from trading_bot.tests.helpers import reset_managers


# TODO add tests
class TestAdapterByBit(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        reset_managers()

        self.symbol = app.symbol_manager.create(
            base_currency='BTC',
            quote_currency='USDT',
            exchanges=[app.exchange_manager.create(name='TestExchange', deal_opening_method='send_message')],
            deal_opening_params={'qty': 0.001}
        )
        self.decision_buy = DecisionMaker.Decision(
            symbol=self.symbol,
            side=DealSide.BUY,
            trading_system=MagicMock()
        )
        self.decision_sell = DecisionMaker.Decision(
            symbol=self.symbol,
            side=DealSide.SELL,
            trading_system=MagicMock()
        )

    async def test_open_deal(self):
        with self.subTest(case='...'):
            pass

    def test__get_symbol_alias(self):
        with self.subTest(case='...'):
            pass

    def test__sing_request_params(self):
        with self.subTest(case='...'):
            pass

    def test__get_stop_loss(self):
        with self.subTest(case='...'):
            pass

    def test__get_take_profit(self):
        with self.subTest(case='...'):
            pass

    async def test__create_order(self):
        with self.subTest(case='...'):
            pass

    async def test__get_open_positions(self):
        with self.subTest(case='...'):
            pass

    async def test__set_stop_orders(self):
        with self.subTest(case='...'):
            pass

    async def test_get_open_deal_list(self):
        with self.subTest(case='...'):
            pass
