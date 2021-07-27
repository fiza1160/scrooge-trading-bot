import unittest
from app.main import CoinRsiInfo, DecisionMaker


class TestDecisionMaker(unittest.TestCase):

    def test_choose_rising_low_rsi(self):
        with self.subTest(case='When previous RSI < 30 and RSI began to rise (present RSI > previous RSI)'
                               'decision list should contain message'):
            rsi_info = [
                CoinRsiInfo(
                    coin='BTC/USDT',
                    present_rsi=32,
                    previous_rsi=28,
                )
            ]
            decisions = DecisionMaker.choose_rising_low_rsi(rsi_info)
            self.assertEqual(len(decisions), 1)
            self.assertEqual(
                decisions[0],
                'BTC/USDT previous RSI: 28, present RSI: 32'
            )

        with self.subTest(case='When previous RSI > 30, an empty list should be returned'):
            rsi_info = [
                CoinRsiInfo(
                    coin='BTC/USDT',
                    present_rsi=32,
                    previous_rsi=40,
                )
            ]
            decisions = DecisionMaker.choose_rising_low_rsi(rsi_info)
            self.assertEqual(len(decisions), 0)

        with self.subTest(case='When previous RSI = 30, an empty list should be returned'):
            rsi_info = [
                CoinRsiInfo(
                    coin='BTC/USDT',
                    present_rsi=42,
                    previous_rsi=30,
                )
            ]
            decisions = DecisionMaker.choose_rising_low_rsi(rsi_info)
            self.assertEqual(len(decisions), 0)

        with self.subTest(case='When previous RSI < 30, but present RSI < previous RSI, '
                               'an empty list should be returned'):
            rsi_info = [
                CoinRsiInfo(
                    coin='BTC/USDT',
                    present_rsi=11,
                    previous_rsi=19,
                )
            ]
            decisions = DecisionMaker.choose_rising_low_rsi(rsi_info)
            self.assertEqual(len(decisions), 0)

        with self.subTest(case='When previous RSI < 30, but present RSI = previous RSI, '
                               'an empty list should be returned'):
            rsi_info = [
                CoinRsiInfo(
                    coin='BTC/USDT',
                    present_rsi=19,
                    previous_rsi=19,
                )
            ]
            decisions = DecisionMaker.choose_rising_low_rsi(rsi_info)
            self.assertEqual(len(decisions), 0)

        with self.subTest(case='When previous RSI > 30, and present RSI > 30, '
                               'an empty list should be returned'):
            rsi_info = [
                CoinRsiInfo(
                    coin='BTC/USDT',
                    present_rsi=42,
                    previous_rsi=65,
                )
            ]
            decisions = DecisionMaker.choose_rising_low_rsi(rsi_info)
            self.assertEqual(len(decisions), 0)
