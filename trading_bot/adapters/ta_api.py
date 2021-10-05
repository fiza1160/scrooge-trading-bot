import asyncio
import logging
import requests

from trading_bot.models.indicators import Indicator
from trading_bot.models.symbols import Symbol

logger = logging.getLogger('logger')


class AdapterTaAPI:

    def __init__(self, api_key: str, timeout: int) -> None:
        self._api_key = api_key
        self._timeout = timeout
        self._symbol_template = '{base_currency}/{quote_currency}'
        self._url = 'https://api.taapi.io/'
        self._endpoints = {
            'Momentum': 'mom',
            'MovingAverage': 'ma',
            'ParabolicSAR': 'sar',
        }

    async def get_indicator_values(self, symbol: Symbol, indicator: Indicator) -> {}:

        await asyncio.sleep(self._timeout)

        params = {
            'secret': self._api_key,
            'exchange': 'binance',
            'symbol': self._get_symbol_alias(symbol),
            'interval': indicator.interval.name,
            'backtracks': 2,
        }

        if indicator.period:
            params['optInTimePeriod'] = indicator.period

        url = f'{self._url}{self._endpoints.get(indicator.indicator_type)}'
        response = requests.get(url, params=params)
        if response.status_code != 200:
            logger.warning(f'{symbol} {response.text}\n'
                         f'{indicator}')
            raise Warning

        resp = self._parse_response(response=response.json())
        logger.info(f'{symbol} {indicator} {resp}')

        return resp

    def _get_symbol_alias(self, symbol: Symbol) -> str:
        return self._symbol_template.format(
            base_currency=symbol.base_currency,
            quote_currency=symbol.quote_currency,
        )

    @staticmethod
    def _parse_response(response: {}) -> {}:

        present_value = 0
        previous_value = 0

        for item in response:
            backtrack = item.get('backtrack')

            if backtrack == 0:
                present_value = item.get('value')
            elif backtrack == 1:
                previous_value = item.get('value')

        return {
            'present_value': present_value,
            'previous_value': previous_value,
        }
