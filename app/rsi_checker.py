import asyncio
import time

import aiohttp as aiohttp


class IndicatorInfoRSI:

    def __init__(self, future, present_value=0, previous_value=0):
        self.future = future
        self.present_value = int(present_value)
        self.previous_value = int(previous_value)
        self.indicator_name = 'RSI'

    def __str__(self):
        return f'{self.future} present {self.indicator_name}: {self.present_value}, ' \
               f'previous {self.indicator_name}: {self.previous_value}'


class IndicatorCheckerRSI:

    def __init__(self, futures, ta_api_key, timeout):
        self.futures = futures
        self.ta_api_key = ta_api_key
        self.timeout = timeout

    async def check(self, rsi_queue):
        while True:
            for future in self.futures:
                response = await self._make_request(future)
                if response:
                    rsi_info = await self._parse_response(future, response)
                    await rsi_queue.put(rsi_info)

            await asyncio.sleep(60)

    async def _make_request(self, future):

        await asyncio.sleep(self.timeout)

        params = {
            'secret': self.ta_api_key,
            'exchange': 'binance',
            'symbol': future,
            'interval': '5m',
            'backtracks': 2,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.taapi.io/rsi', params=params) as resp:
                if resp.status != 200:
                    # TODO add logger
                    print(f'{time.strftime("%H:%M:%S", time.localtime())} -{future}- {await resp.text()}')
                    return

                resp_json = await resp.json()

        return resp_json

    @staticmethod
    async def _parse_response(future, response):

        present_rsi = 0
        previous_rsi = 0

        for item in response:
            backtrack = item.get('backtrack')

            if backtrack == 0:
                present_rsi = item.get('value')
            elif backtrack == 1:
                previous_rsi = item.get('value')

        return IndicatorInfoRSI(
            future=future,
            present_value=present_rsi,
            previous_value=previous_rsi,
        )