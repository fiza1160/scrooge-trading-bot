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
            decisions = self.decision_maker.choose_low_rsi(coins_rsi)
            for decision in decisions:
                self.notifier.notify(decision)
            time.sleep(60)


class RsiChecker:

    def __init__(self, ta_api_key, coins, timeout):
        self.ta_api_key = ta_api_key
        self.coins = coins
        self.timeout = timeout

    def check_rsi(self):
        coins_rsi = {}
        for coin in self.coins:
            rsi = self._get_coin_rsi(coin)
            if rsi:
                coins_rsi[coin] = int(rsi)

        return coins_rsi

    def _get_coin_rsi(self, coin):
        rsi = None

        time.sleep(self.timeout)

        payload = {
            'secret': self.ta_api_key,
            'exchange': 'binance',
            'symbol': coin,
            'interval': '5m',
        }
        r = requests.get('https://api.taapi.io/rsi', params=payload)

        if r.status_code == requests.codes.ok:
            rsi = r.json().get('value')

        return rsi


class DecisionMaker:

    @staticmethod
    def choose_low_rsi(coins_rsi):
        decisions = []
        for coin in coins_rsi:
            rsi = coins_rsi.get(coin)
            if rsi < 30:
                decisions.append(f'{coin} RSI: {rsi}')

        return decisions


class Notifier:

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(self.token)

    def notify(self, message):
        self.bot.send_message(self.chat_id, message)
