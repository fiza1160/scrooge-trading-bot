import hashlib
import hmac
import time

import requests

from trading_bot import app
from trading_bot.models.symbols import Symbol
from trading_bot.services.decision_maker import DealSide


class AdapterByBit:
    def __init__(self, api_key: str, api_secret: str):
        self._api_key = api_key
        self._api_secret = api_secret
        self._symbol_template = '{base_currency}{quote_currency}'
        self._url = 'https://api-testnet.bybit.com//'

    async def open_deal(self, decision):

        await self._create_order(
            side=decision.side,
            symbol=decision.symbol,
        )

        position_info = await self._get_position_info(
            symbol=decision.symbol,
            side=decision.side,
        )

        entry_price = position_info['entry_price']

        await self._set_stop_orders(
            side=decision.side,
            symbol=decision.symbol,
            entry_price=entry_price,
        )

        # TODO add logger
        msg = f'I just opened a deal (ByBit). ({decision})'
        print(msg)

        await app.notifier.notify(msg=msg)

    async def _create_order(
            self,
            side: DealSide,
            symbol: Symbol,
    ):

        timestamp_ms = int(time.time() * 1000.0)
        params = {
            'api_key': self._api_key,
            'close_on_trigger': False,
            'order_type': 'Market',
            'qty': symbol.deal_opening_params.qty,
            'reduce_only': False,
            'side': side.name.capitalize(),
            'symbol': self._get_symbol_alias(symbol),
            'time_in_force': 'GoodTillCancel',
            'timestamp': timestamp_ms,
        }

        params['sign'] = self._sing_request_params(params)

        url = f'{self._url}private/linear/order/create'
        response = requests.post(url, params=params)
        resp = response.json()

        if resp['ret_msg'] != 'OK':
            # TODO add logger
            print(f'ret_code: {resp["ret_code"]} msg: {resp["ret_msg"]}')
            raise RuntimeError

        return resp

    def _get_symbol_alias(self, symbol):
        return self._symbol_template.format(
            base_currency=symbol.base_currency,
            quote_currency=symbol.quote_currency,
        )

    def _sing_request_params(self, params):
        ordered_params = ""
        for key in sorted(params):
            ordered_params += f'{key}={params[key]}&'
        ordered_params = ordered_params[:-1]

        return hmac.new(
            bytes(self._api_secret, "utf-8"),
            ordered_params.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    async def _get_position_info(
            self,
            symbol: Symbol,
            side: DealSide
    ):
        resp = await self._get_position_by_symbol(symbol)

        if side is DealSide.BUY:
            position_info = resp['result'][0]
        else:
            position_info = resp['result'][1]

        return position_info

    async def _get_position_by_symbol(self, symbol):
        timestamp_ms = int(time.time() * 1000.0)
        params = {
            'api_key': self._api_key,
            'symbol': self._get_symbol_alias(symbol),
            'timestamp': timestamp_ms,
        }
        params['sign'] = self._sing_request_params(params)
        url = f'{self._url}private/linear/position/list'
        response = requests.get(url, params=params)
        resp = response.json()
        if resp['ret_msg'] != 'OK':
            # TODO add logger
            print(f'ret_code: {resp["ret_code"]} msg: {resp["ret_msg"]}')
            raise RuntimeError
        return resp

    async def _set_stop_orders(
            self,
            side: DealSide,
            symbol: Symbol,
            entry_price: float
    ):
        stop_loss = self._get_stop_loss(side, entry_price)
        take_profit = self._get_take_profit(side, entry_price)

        timestamp_ms = int(time.time() * 1000.0)
        params = {
            'api_key': self._api_key,
            'side': side.name.capitalize(),
            'stop_loss': stop_loss,
            'symbol': self._get_symbol_alias(symbol),
            'take_profit': take_profit,
            'timestamp': timestamp_ms,
        }

        params['sign'] = self._sing_request_params(params)

        url = f'{self._url}private/linear/position/trading-stop'
        response = requests.post(url, params=params)
        resp = response.json()

        if resp['ret_msg'] != 'OK':
            # TODO add logger
            print(f'ret_code: {resp["ret_code"]} msg: {resp["ret_msg"]}')
            raise RuntimeError

        return resp

    @staticmethod
    def _get_stop_loss(
            side: DealSide,
            entry_price: float
    ):
        sl_percent = 0.01
        if side is DealSide.BUY:
            sl_price = entry_price * (1 - sl_percent)
        else:
            sl_price = entry_price * (1 + sl_percent)

        return round(sl_price, 2)

    @staticmethod
    def _get_take_profit(
            side: DealSide,
            entry_price: float
    ):
        tp_percent = 0.01
        if side is DealSide.BUY:
            tp_price = entry_price * (1 + tp_percent)
        else:
            tp_price = entry_price * (1 - tp_percent)

        return round(tp_price, 2)

    async def symbol_has_open_deal(self, symbol):
        response = await self._get_position_by_symbol(symbol)

        has_open_deals = False
        for res in response.get('result'):
            if res['size'] != 0:
                has_open_deals = True

        return has_open_deals
