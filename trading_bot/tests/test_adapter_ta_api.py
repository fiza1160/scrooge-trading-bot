import json
import os
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, Mock

from trading_bot import app
from trading_bot.adapters.ta_api import AdapterTaAPI
from trading_bot.tests.helpers import reset_managers

base_dir = os.path.abspath(os.path.dirname(__file__))
settings_dir = f'{base_dir}\\static'


class TaAPIResponseLoader:

    @staticmethod
    def response():
        with open(f'{settings_dir}\\ta_api_response.json') as f:
            return json.load(f)


class TestAdapterTaAPI(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        reset_managers()

    @patch('trading_bot.adapters.ta_api.print')
    @patch('trading_bot.adapters.ta_api.requests.get')
    async def test_get_indicator_values(self, mock_get, mock_print):
        with self.subTest(case='Check request params and returned indicator values'):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = TaAPIResponseLoader.response()

            mock_get.return_value = mock_response

            app.exchange_manager.create(name='ByBit', deal_opening_method='open_deal')

            symbol = app.symbol_manager.create(
                base_currency='BTC',
                quote_currency='USDT',
                exchanges='ByBit',
                deal_opening_params={'qty': 0.368}
            )

            indicator = app.indicator_manager.create(
                name='1h_Momentum_10',
                indicator_type='Momentum',
                interval='1h',
                period=10,
            )

            test_api_key = 'test api key'
            indicator_values = await AdapterTaAPI(api_key=test_api_key, timeout=0).get_indicator_values(
                symbol=symbol,
                indicator=indicator,
            )

            url = 'https://api.taapi.io/mom'
            params = {
                'secret': test_api_key,
                'exchange': 'binance',
                'symbol': f'{symbol.base_currency}/{symbol.quote_currency}',
                'interval': indicator.interval.name,
                'backtracks': indicator.period,
            }

            mock_get.assert_called_with(url, params=params)

            self.assertEqual(indicator_values['present_value'], 2020.9800000000032)
            self.assertEqual(indicator_values['previous_value'], 2016.9000000000015)

        with self.subTest(case='When response status code != 200, it should print logs'):
            mock_get.return_value = Mock(status_code=400, text='test response text')

            app.exchange_manager.create(name='ByBit', deal_opening_method='open_deal')

            symbol = app.symbol_manager.create(
                base_currency='BTC',
                quote_currency='USDT',
                exchanges='ByBit',
                deal_opening_params={'qty': 0.368}
            )

            indicator = app.indicator_manager.create(
                name='1h_Momentum_10',
                indicator_type='Momentum',
                interval='1h',
                period=10,
            )

            test_api_key = 'test api key'
            await AdapterTaAPI(api_key=test_api_key, timeout=0).get_indicator_values(
                symbol=symbol,
                indicator=indicator,
            )

            mock_print.assert_called_with('BTCUSDT test response text')

    async def test__parse_response(self):
        with self.subTest(case='Test response parser'):
            response = TaAPIResponseLoader.response()

            test_api_key = 'test api key'
            parsed_response = AdapterTaAPI(api_key=test_api_key, timeout=0)._parse_response(response)

            self.assertEqual(parsed_response['present_value'], 2020.9800000000032)
            self.assertEqual(parsed_response['previous_value'], 2016.9000000000015)
