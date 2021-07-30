import asyncio
import time

import aiohttp as aiohttp
import telebot


class App:

    def __init__(self, rsi_checker, decision_maker, notifier):
        self.rsi_checker = rsi_checker
        self.decision_maker = decision_maker
        self.notifier = notifier

    def run(self) -> None:
        asyncio.run(self._create_tasks())

    async def _create_tasks(self):
        rsi_queue = asyncio.Queue()
        decision_queue = asyncio.Queue()

        rsi_checker_task = asyncio.create_task(self.rsi_checker.check(rsi_queue), name='RSI Checker')
        decision_maker_task = asyncio.create_task(self.decision_maker.choose_rising_low_rsi(rsi_queue, decision_queue),
                                             name='Decision Maker')
        notifier_task = asyncio.create_task(self.notifier.notify(decision_queue), name='Notifier')

        await asyncio.gather(
            rsi_checker_task,
            decision_maker_task,
            notifier_task,
        )


class IndicatorInfoRSI:

    def __init__(self, coin, present_value=0, previous_value=0):
        self.coin = coin
        self.present_value = int(present_value)
        self.previous_value = int(previous_value)
        self.indicator_name = 'RSI'

    def __str__(self):
        return f'{self.coin} present {self.indicator_name}: {self.present_value}, ' \
               f'previous {self.indicator_name}: {self.previous_value}'


class IndicatorCheckerRSI:

    def __init__(self, coins, ta_api_key, timeout):
        self.coins = coins
        self.ta_api_key = ta_api_key
        self.timeout = timeout

    async def check(self, rsi_queue):
        while True:
            for coin in self.coins:
                response = await self._make_request(coin)
                if response:
                    rsi_info = await self._parse_response(coin, response)
                    await rsi_queue.put(rsi_info)

            await asyncio.sleep(60)

    async def _make_request(self, coin):

        await asyncio.sleep(self.timeout)

        params = {
            'secret': self.ta_api_key,
            'exchange': 'binance',
            'symbol': coin,
            'interval': '5m',
            'backtracks': 2,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.taapi.io/rsi', params=params) as resp:
                if resp.status != 200:
                    # TODO add logger
                    print(f'{time.strftime("%H:%M:%S", time.localtime())} -{coin}- {await resp.text()}')
                    return

                resp_json = await resp.json()

        return resp_json

    @staticmethod
    async def _parse_response(coin, response):

        present_rsi = 0
        previous_rsi = 0

        for item in response:
            backtrack = item.get('backtrack')

            if backtrack == 0:
                present_rsi = item.get('value')
            elif backtrack == 1:
                previous_rsi = item.get('value')

        return IndicatorInfoRSI(
            coin=coin,
            present_value=present_rsi,
            previous_value=previous_rsi,
        )


class DecisionMaker:

    @staticmethod
    async def choose_rising_low_rsi(rsi_queue: asyncio.Queue,
                                    decision_queue: asyncio.Queue) -> None:
        while True:
            rsi = await rsi_queue.get()
            if rsi.present_value > rsi.previous_value < 30:
                await decision_queue.put(str(rsi))

            rsi_queue.task_done()


class Notifier:

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(self.token)

    async def notify(self, decision_queue):
        while True:
            message = await decision_queue.get()
            self.bot.send_message(self.chat_id, message)
            decision_queue.task_done()
