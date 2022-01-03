import logging
from typing import Dict

from trading_bot import AdapterTaAPI
from trading_bot.models.indicators import Indicator
from trading_bot.models.symbols import Symbol

logger = logging.getLogger('logger')


class IndicatorInformer:
    def __init__(self, indicators_adapter: AdapterTaAPI) -> None:
        self._indicators_adapter = indicators_adapter

    async def get_indicator_values(self, symbol: Symbol, indicator: Indicator) -> Dict[str, float]:
        try:
            return await self._indicators_adapter.get_indicator_values(symbol=symbol, indicator=indicator)
        except Warning:
            logger.warning(f'I did not get {indicator} values for {symbol}')
            raise Warning

