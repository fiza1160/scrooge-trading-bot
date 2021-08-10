import asyncio
from unittest import IsolatedAsyncioTestCase

from app.exchanges import create_exchange_list
from app.symbols import Symbol
from app.workers.decition_maker import Side
from app.workers.rsi_checker import IndicatorInfoRSI
from app import DecisionMaker


class TestDecisionMaker(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.decision_maker = DecisionMaker()
        self.rsi_queue = asyncio.Queue()
        self.decision_queue = asyncio.Queue()
        self.symbol = Symbol(
            exchanges=create_exchange_list(['stormgain','bybit']),
            base_currency='BTC',
            quote_currency='USDT',
        )

        asyncio.create_task(
            self.decision_maker.choose_rising_low_rsi(self.rsi_queue, self.decision_queue),
            name='Decision Maker'
        )

    async def _put_rsi_in_queue(self, present_value, previous_value):

        rsi_info = IndicatorInfoRSI(
            symbol=self.symbol,
            present_value=present_value,
            previous_value=previous_value,
        )

        self.rsi_queue.put_nowait(rsi_info)
        await asyncio.sleep(1)

    async def test_choose_rising_low_rsi(self):
        with self.subTest(case='When previous RSI < 30 and RSI began to rise (present RSI > previous RSI)'
                               'decision list should contain message'):
            await self._put_rsi_in_queue(present_value=32, previous_value=28)

            self.assertEqual(self.decision_queue.empty(), False)

            decision = self.decision_queue.get_nowait()
            self.assertEqual(decision.symbol, self.symbol)
            self.assertEqual(decision.side, Side.Buy)
            self.assertEqual(decision.cause, 'present RSI 32, previous RSI 28')

        with self.subTest(case='When previous RSI > 30, an empty list should be returned'):
            await self._put_rsi_in_queue(present_value=18, previous_value=45)
            self.assertEqual(self.decision_queue.empty(), True)

        with self.subTest(case='When previous RSI = 30, an empty list should be returned'):
            await self._put_rsi_in_queue(present_value=42, previous_value=30)
            self.assertEqual(self.decision_queue.empty(), True)

        with self.subTest(case='When previous RSI < 30, but present RSI < previous RSI, '
                               'an empty list should be returned'):
            await self._put_rsi_in_queue(present_value=11, previous_value=19)
            self.assertEqual(self.decision_queue.empty(), True)

        with self.subTest(case='When previous RSI < 30, but present RSI = previous RSI, '
                               'an empty list should be returned'):
            await self._put_rsi_in_queue(present_value=19, previous_value=19)
            self.assertEqual(self.decision_queue.empty(), True)

        with self.subTest(case='When previous RSI > 30, and present RSI > 30, '
                               'an empty list should be returned'):
            await self._put_rsi_in_queue(present_value=42, previous_value=65)
            self.assertEqual(self.decision_queue.empty(), True)
