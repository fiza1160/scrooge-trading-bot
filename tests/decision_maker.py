import asyncio
from unittest import IsolatedAsyncioTestCase
from app.rsi_checker import IndicatorInfoRSI
from app import DecisionMaker


class TestDecisionMaker(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.decision_maker = DecisionMaker()
        self.rsi_queue = asyncio.Queue()
        self.decision_queue = asyncio.Queue()

        asyncio.create_task(
            self.decision_maker.choose_rising_low_rsi(self.rsi_queue, self.decision_queue),
            name='Decision Maker'
        )

    async def _put_rsi_in_queue(self, present_value, previous_value):
        rsi_info = IndicatorInfoRSI(
            coin='BTC/USDT',
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
            self.assertEqual(
                self.decision_queue.get_nowait(),
                'BTC/USDT present RSI: 32, previous RSI: 28'
            )

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

