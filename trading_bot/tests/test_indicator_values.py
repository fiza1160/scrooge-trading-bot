from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch

from trading_bot import app
from trading_bot.models.indicator_values import IndicatorValueManager
from trading_bot.tests.helpers import reset_managers


class TestIndicatorValueManager(TestCase):

    def setUp(self) -> None:
        reset_managers()

    def test_create(self):
        with self.subTest(case='Try to create IndicatorValue '
                               'indicator should be Momentum'
                               'symbol should be BTCUSDT'
                               'present_value should be 10'
                               'previous_value should be 7.25'):
            indicator = self._create_indicator()
            symbol = self._create_symbol()

            with patch('trading_bot.models.indicator_values.datetime') as mock_datetime:
                datetime_now = datetime.now()
                mock_datetime.now.return_value = datetime_now

                indicator_value = IndicatorValueManager().create(
                    indicator=indicator,
                    symbol=symbol,
                    present_value=10,
                    previous_value=7.25
                )

                self.assertEqual(indicator_value.indicator, indicator)
                self.assertEqual(indicator_value.symbol, symbol)
                self.assertEqual(indicator_value.present_value, 10)
                self.assertEqual(indicator_value.previous_value, 7.25)
                self.assertEqual(indicator_value.updated_at, datetime_now)

    @staticmethod
    def _create_symbol(base_currency='BTC'):
        app.exchange_manager.create(
            name='ByBit',
            deal_opening_method='open_deal'
        )
        symbol = app.symbol_manager.create(
            base_currency=base_currency,
            quote_currency='USDT',
            exchanges=['ByBit'],
            deal_opening_params={'qty': 2}
        )
        return symbol

    @staticmethod
    def _create_indicator(name='1h_Momentum_10'):
        return app.indicator_manager.create(
            name=name,
            indicator_type='Momentum',
            interval='1h',
            period=10,
        )

    def test_get(self):
        with self.subTest(case='New and empty IndicatorValueManager should return None'):
            iv_manager = IndicatorValueManager()

            indicator = self._create_indicator()
            symbol = self._create_symbol()

            self.assertIsNone(iv_manager.get(indicator=indicator, symbol=symbol))

        with self.subTest(case='If IndicatorValue exists '
                               'IndicatorValueManager should return right IndicatorValue object'):

            iv_manager = IndicatorValueManager()

            indicators = [
                self._create_indicator(name=f'1h_Momentum_10'),
                self._create_indicator(name=f'1h_MovingAverage_4')
            ]

            symbols = [
                self._create_symbol(),
                self._create_symbol(base_currency='ETH')
            ]

            for indicator in indicators:
                for symbol in symbols:
                    iv_manager.create(
                        indicator=indicator,
                        symbol=symbol,
                        previous_value=1,
                        present_value=11,
                    )

            ind_values = iv_manager.get(
                indicator=indicators[0],
                symbol=symbols[0],
            )

            self.assertEqual(ind_values.indicator, indicators[0])
            self.assertEqual(ind_values.symbol, symbols[0])

        with self.subTest(case='If IndicatorValue does not exist '
                               'IndicatorValueManager should return None'):

            iv_manager = IndicatorValueManager()

            mom = self._create_indicator(name=f'1h_Momentum_10')
            ma = self._create_indicator(name=f'1h_MovingAverage_4')

            bch = self._create_symbol(base_currency='BCH')
            eth = self._create_symbol(base_currency='ETH')

            iv_manager.create(
                indicator=mom,
                symbol=bch,
                previous_value=1,
                present_value=11,
            )

            iv_manager.create(
                indicator=mom,
                symbol=eth,
                previous_value=1,
                present_value=11,
            )

            self.assertIsNone(iv_manager.get(indicator=ma, symbol=eth))

    def test_update(self):
        with self.subTest(case='When IndicatorValue exists, '
                               'IndicatorValueManager should update right IndicatorValue object'):
            iv_manager = IndicatorValueManager()

            indicators = [
                self._create_indicator(name=f'1h_Momentum_10'),
                self._create_indicator(name=f'1h_MovingAverage_4')
            ]

            symbols = [
                self._create_symbol(),
                self._create_symbol(base_currency='ETH')
            ]

            value = 0
            for indicator in indicators:
                for symbol in symbols:
                    iv_manager.create(
                        indicator=indicator,
                        symbol=symbol,
                        previous_value=value,
                        present_value=value + 1,
                    )
                    value += 2

            with patch('trading_bot.models.indicator_values.datetime') as mock_datetime:
                datetime_now = datetime.now()
                mock_datetime.now.return_value = datetime_now

                updated_values = iv_manager.update(
                    indicator=indicators[0],
                    symbol=symbols[0],
                    present_value=66.4,
                    previous_value=22,
                )

                self.assertEqual(updated_values.indicator, indicators[0])
                self.assertEqual(updated_values.symbol, symbols[0])
                self.assertEqual(updated_values.present_value, 66.4)
                self.assertEqual(updated_values.previous_value, 22)
                self.assertEqual(updated_values.updated_at, datetime_now)

        with self.subTest(case='When IndicatorValue does not exist, '
                               'IndicatorValueManager should create new IndicatorValue object'):
            iv_manager = IndicatorValueManager()

            mom = self._create_indicator(name=f'1h_Momentum_10')
            ma = self._create_indicator(name=f'1h_MovingAverage_4')

            bch = self._create_symbol(base_currency='BCH')
            eth = self._create_symbol(base_currency='ETH')

            iv_manager.create(
                indicator=mom,
                symbol=bch,
                previous_value=1,
                present_value=11,
            )

            iv_manager.create(
                indicator=mom,
                symbol=eth,
                previous_value=1,
                present_value=11,
            )

            updated_ind_values = iv_manager.update(
                indicator=ma,
                symbol=eth,
                present_value=800,
                previous_value=-300,
            )

            self.assertEqual(updated_ind_values.indicator, ma)
            self.assertEqual(updated_ind_values.symbol, eth)
            self.assertEqual(updated_ind_values.present_value, 800)
            self.assertEqual(updated_ind_values.previous_value, -300)

    def test_list(self):
        with self.subTest(case='New and empty IndicatorValueManager should return empty list'):
            self.assertEqual(len(IndicatorValueManager().list()), 0)

        with self.subTest(case='Try to create indicator value '
                               'IndicatorValueManager should return list with the indicator value'):
            iv_manager = IndicatorValueManager()

            indicator = self._create_indicator()
            symbol = self._create_symbol()

            ind_value = iv_manager.create(
                indicator=indicator,
                symbol=symbol,
                previous_value=8,
                present_value=18,
            )

            self.assertEqual(len(iv_manager.list()), 1)
            self.assertIn(ind_value, iv_manager.list())

        with self.subTest(case='Try to create 4 indicator values '
                               'IndicatorValueManager should return list with 10 indicator values'):
            iv_manager = IndicatorValueManager()

            indicators = [
                self._create_indicator(name=f'1h_Momentum_10'),
                self._create_indicator(name=f'1h_MovingAverage_4')
            ]

            symbols = [
                self._create_symbol(),
                self._create_symbol(base_currency='ETH')
            ]

            created_ind_values = []
            for indicator in indicators:
                for symbol in symbols:
                    created_ind_values.append(
                        iv_manager.create(
                            indicator=indicator,
                            symbol=symbol,
                            previous_value=8,
                            present_value=18,
                        )
                    )

            self.assertEqual(len(iv_manager.list()), 4)
            self.assertEqual(iv_manager.list(), created_ind_values)


class TestIndicatorValue(TestCase):

    def setUp(self) -> None:
        reset_managers()

    @patch('trading_bot.models.indicator_values.datetime')
    def test_is_actual(self, mock_datetime):
        datetime_now = datetime.now()
        mock_datetime.now.return_value = datetime_now

        btc = app.symbol_manager.create(
            base_currency='BTC',
            quote_currency='USDT',
            exchanges=app.exchange_manager.create('Test', 'open_deal'),
            deal_opening_params={'qty': 2}
        )

        mom = app.indicator_manager.create(
            name='1h_Momentum_10',
            indicator_type='Momentum',
            interval='1h',
            period=10,
        )

        indicator_value = app.indicator_value_manager.create(
            indicator=mom,
            symbol=btc,
            present_value=0.45,
            previous_value=-56
        )

        with self.subTest(case='When indicator is actual, method should return True'):
            self.assertTrue(indicator_value.is_actual())
        with self.subTest(case='When indicator is not actual, method should return False'):
            indicator_value.updated_at = datetime_now - timedelta(minutes=65)
            self.assertFalse(indicator_value.is_actual())
