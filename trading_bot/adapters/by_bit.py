import hashlib
import hmac
import time
import logging

import requests

from trading_bot.models.symbols import Symbol
from trading_bot.services.decision_maker import DealSide

logger = logging.getLogger('logger')


class AdapterByBit:

    def __init__(self, api_key: str, api_secret: str):
        self._api_key = api_key
        self._api_secret = api_secret
        self.symbol_template = '{base_currency}{quote_currency}'
        self._url = 'https://api-testnet.bybit.com//'

    async def get_current_price(
            self,
            symbol: Symbol,
    ) -> float:

        params = {
            'symbol': self._get_symbol_alias(symbol),
        }
        url = f'{self._url}/v2/public/tickers'
        response = requests.get(url, params=params)

        resp = response.json()
        if resp['ret_msg'] != 'OK':
            logger.warning(f'ret_code: {resp["ret_code"]} msg: {resp["ret_msg"]}\n'
                         f'{params}')
            raise Warning

        current_price = float(resp['result'][0]['last_price'])

        return current_price

    async def create_order(
            self,
            side: DealSide,
            symbol: Symbol,
            stop_loss: float,
    ):

        timestamp_ms = int(time.time() * 1000.0)

        params = {
            'api_key': self._api_key,
            'close_on_trigger': False,
            'order_type': 'Market',
            'qty': symbol.deal_opening_params.qty,
            'reduce_only': False,
            'side': side.name.capitalize(),
            'stop_loss': stop_loss,
            'symbol': self._get_symbol_alias(symbol),
            'time_in_force': 'GoodTillCancel',
            'timestamp': timestamp_ms,
        }

        params['sign'] = self._sing_request_params(params)

        url = f'{self._url}private/linear/order/create'
        response = requests.post(url, params=params)
        resp = response.json()

        if resp['ret_msg'] != 'OK':
            logger.warning(f'ret_code: {resp["ret_code"]} msg: {resp["ret_msg"]}\n'
                         f'{params}')
            raise Warning

        return resp

    def _get_symbol_alias(self, symbol):
        return self.symbol_template.format(
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

    async def get_positions_by_symbol(self, symbol):
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
            logger.warning(f'ret_code: {resp["ret_code"]} msg: {resp["ret_msg"]}\n'
                         f'{params}')
            raise Warning
        return resp

    async def set_stop_loss(self, deal, stop_loss):
        timestamp_ms = int(time.time() * 1000.0)

        params = {
            'api_key': self._api_key,
            'side': deal.side.name.capitalize(),
            'stop_loss': round(stop_loss, 0),
            'symbol': self._get_symbol_alias(deal.symbol),
            'timestamp': timestamp_ms,
        }

        params['sign'] = self._sing_request_params(params)

        url = f'{self._url}private/linear/position/trading-stop'
        response = requests.post(url, params=params)
        resp = response.json()

        if resp['ret_msg'] != 'OK':
            logger.warning(f'ret_code: {resp["ret_code"]} msg: {resp["ret_msg"]}\n'
                         f'{params}')
            raise Warning

        return resp
