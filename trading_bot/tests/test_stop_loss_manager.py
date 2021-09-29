# TODO add tests
from unittest import IsolatedAsyncioTestCase

from trading_bot import app
from trading_bot.adapters.by_bit import AdapterByBit
from trading_bot.adapters.ta_api import AdapterTaAPI
from trading_bot.models.indicators import IndicatorManager
from trading_bot.models.symbols import SymbolManager
from trading_bot.services.stop_loss_manager import StopLossManager
from trading_bot.tests.helpers import reset_managers


class TestStopLossManager(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        reset_managers()

    async def test__update_stop_losses(self):
        with self.subTest(case='...'):
            pass

    async def test__get_symbols_with_open_deals(self):
        with self.subTest(case='...'):
            pass

    async def test__get_new_stop_loss_value(self):
        with self.subTest(case='...'):
            pass
