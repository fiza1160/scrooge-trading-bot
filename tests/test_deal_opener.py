import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from app import DealOpeningRouter

from tests.fabrics import SymbolFabric, DecisionFabric


class TestDealOpeningRouter(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.deal_opening_router = DealOpeningRouter()
        self.decision_queue = asyncio.Queue()
        self.message_queue = asyncio.Queue()
        self.deal_queue = asyncio.Queue()

        asyncio.create_task(
            self.deal_opening_router.route_deal(self.decision_queue, self.message_queue, self.deal_queue),
            name='Deal Opener',
        )

    async def _put_decision_in_queue(self, symbol=None):
        self.decision = DecisionFabric.create(symbol=symbol)

        self.decision_queue.put_nowait(self.decision)
        await asyncio.sleep(1)

    @patch('builtins.print')
    async def test_open_deal(self, mock_print):
        with self.subTest(case='If Symbol with only one Exchange '
                               'and DealOpeningMethod is SEND_MESSAGE '
                               'message_queue should contain message, '
                               'deal_queue should be empty'):

            symbol = SymbolFabric.create(exchange_list=['stormgain'])
            await self._put_decision_in_queue(symbol)

            self.assertEqual(self.message_queue.empty(), False)
            message = self.message_queue.get_nowait()
            self.assertEqual(message, str(self.decision))

            self.assertEqual(self.deal_queue.empty(), True)

        with self.subTest(case='If Symbol with only one Exchange '
                               'and DealOpeningMethod is CREATE_ORDER '
                               'message_queue should be empty, '
                               'deal_queue should contain order'):

            symbol = SymbolFabric.create(exchange_list=['bybit'])
            await self._put_decision_in_queue(symbol)

            self.assertEqual(self.deal_queue.empty(), False)
            order = self.deal_queue.get_nowait()
            self.assertEqual(order, self.decision)

            self.assertEqual(self.message_queue.empty(), True)

        with self.subTest(case='If Symbol with two Exchanges '
                               'with different DealOpeningMethod (CREATE_ORDER and SEND_MESSAGE) '
                               'message_queue should contain message, '
                               'deal_queue should contain order'):

            await self._put_decision_in_queue()

            self.assertEqual(self.deal_queue.empty(), False)
            order = self.deal_queue.get_nowait()
            self.assertEqual(order, self.decision)

            self.assertEqual(self.message_queue.empty(), False)
            message = self.message_queue.get_nowait()
            self.assertEqual(message, str(self.decision))

        with self.subTest(case='If DealOpeningMethod is not implemented (not CREATE_ORDER and not SEND_MESSAGE) '
                               'message_queue should be empty, '
                               'deal_queue should be empty, '
                               'message should be printed'):

            symbol = SymbolFabric.create_with_test_exchange()
            await self._put_decision_in_queue(symbol)

            mock_print.assert_called_with('DealOpeningMethod TEST is not implemented')
