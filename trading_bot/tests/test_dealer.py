# TODO add tests
from unittest import IsolatedAsyncioTestCase


from trading_bot.tests.helpers import reset_managers


class TestDealer(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        reset_managers()

    async def test_open_deal(self):
        with self.subTest(case='...'):
            pass

    def test__count_stop_loss_value(self):
        with self.subTest(case='...'):
            pass

    async def test_symbol_has_open_deal(self):
        with self.subTest(case='...'):
            pass

    async def test_get_deals_by_symbol(self):
        with self.subTest(case='...'):
            pass

    async def test_set_stop_loss(self):
        with self.subTest(case='...'):
            pass