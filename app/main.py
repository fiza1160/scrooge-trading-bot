import time
import requests
import telebot


class App:
    def __init__(self, notifier, rsi_checker, decision_maker):
        self.notifier = notifier
        self.rsi_checker = rsi_checker
        self.decision_maker = decision_maker

    def run(self):
        while True:
            coins_rsi = self.rsi_checker.check_rsi()
            decisions = self.decision_maker.choose_rising_low_rsi(coins_rsi)
            for decision in decisions:
                self.notifier.notify(decision)
            time.sleep(60)


class CoinRsiInfo:

    def __init__(self, coin, present_rsi=0, previous_rsi=0):
        self.coin = coin
        self.present_rsi = present_rsi
        self.previous_rsi = previous_rsi


class RsiChecker:

    def __init__(self, ta_api_key, coins, timeout):
        self.ta_api_key = ta_api_key
        self.coins = coins
        self.timeout = timeout

    def check_rsi(self):
        coins_rsi = []
        for coin in self.coins:
            coin_rsi = self._get_coin_rsi(coin)
            if coin_rsi:
                coins_rsi.append(coin_rsi)

        return coins_rsi

    def _get_coin_rsi(self, coin):

        time.sleep(self.timeout)
        rsi_values = self._get_rsi_values(coin)

        if rsi_values:
            return CoinRsiInfo(
                coin=coin,
                present_rsi=rsi_values['present_rsi'],
                previous_rsi=rsi_values['previous_rsi']
            )

    def _get_rsi_values(self, coin):
        payload = {
            'secret': self.ta_api_key,
            'exchange': 'binance',
            'symbol': coin,
            'interval': '5m',
            'backtracks': 2,
        }
        r = requests.get('https://api.taapi.io/rsi', params=payload)
        if r.status_code != requests.codes.ok:
            print(f'{time.strftime("%H:%M:%S", time.localtime())} -{coin}- {r.content}')  # TODO add logger
            if r.status_code == 429:
                time.sleep(60)
            return

        return self._parse_response(r.json())

    @staticmethod
    def _parse_response(response):

        rsi_values = {
            'present_rsi': 0,
            'previous_rsi': 0,
        }

        for item in response:
            backtrack = item.get('backtrack')

            if backtrack == 0:
                rsi_values['present_rsi'] = item.get('value')
            elif backtrack == 1:
                rsi_values['previous_rsi'] = item.get('value')

        return rsi_values


class DecisionMaker:

    @staticmethod
    def choose_rising_low_rsi(coins_rsi):
        decisions = []
        for rsi in coins_rsi:
            if rsi.present_rsi > rsi.previous_rsi < 30:
                decisions.append(f'{rsi.coin} previous RSI: {rsi.previous_rsi}, present RSI: {rsi.present_rsi}')

        return decisions


class Notifier:

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(self.token)

    def notify(self, message):
        self.bot.send_message(self.chat_id, message)
