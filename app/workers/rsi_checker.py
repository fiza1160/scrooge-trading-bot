import asyncio

import aiohttp as aiohttp


class IndicatorInfoRSI:

    def __init__(self, symbol, present_value=0, previous_value=0):
        self.symbol = symbol
        self.present_value = int(present_value)
        self.previous_value = int(previous_value)
        self.indicator_name = 'RSI'

    def __str__(self):
        return f'present {self.indicator_name} {self.present_value}, ' \
               f'previous {self.indicator_name} {self.previous_value}'

    def __repr__(self):
        return f'{self.symbol} present {self.indicator_name} {self.present_value}, ' \
               f'previous {self.indicator_name} {self.previous_value}'


class IndicatorCheckerRSI:

    def __init__(self, symbols, ta_api_key, timeout):
        self._symbols = symbols
        self._ta_api_key = ta_api_key
        self._timeout = timeout

    async def check(self, rsi_queue):
        while True:
            for symbol in self._symbols:
                response = await self._make_request(symbol)
                if response:
                    rsi_info = await self._parse_response(symbol, response)
                    await rsi_queue.put(rsi_info)

            await asyncio.sleep(60)

    async def _make_request(self, symbol):

        await asyncio.sleep(self._timeout)

        params = {
            'secret': self._ta_api_key,
            'exchange': 'binance',
            'symbol': self._get_ta_api_symbol_alias(symbol),
            'interval': '5m',
            'backtracks': 2,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.taapi.io/rsi', params=params) as resp:
                if resp.status != 200:
                    # TODO add logger
                    print(f'{symbol} {await resp.text()}')
                    return

                resp_json = await resp.json()

        return resp_json

    @staticmethod
    def _get_ta_api_symbol_alias(symbol):
        return f'{symbol.base_currency}/{symbol.quote_currency}'

    @staticmethod
    async def _parse_response(symbol, response):

        present_rsi = 0
        previous_rsi = 0

        for item in response:
            backtrack = item.get('backtrack')

            if backtrack == 0:
                present_rsi = item.get('value')
            elif backtrack == 1:
                previous_rsi = item.get('value')

        return IndicatorInfoRSI(
            symbol=symbol,
            present_value=present_rsi,
            previous_value=previous_rsi,
        )
