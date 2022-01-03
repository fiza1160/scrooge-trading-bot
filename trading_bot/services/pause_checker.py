import asyncio
import logging

from trading_bot import app, Dealer

logger = logging.getLogger('logger')


class PauseChecker:
    def __init__(self, dealer: Dealer) -> None:
        self._dealer = dealer

    async def run(self) -> None:
        while True:
            await self._check_open_deals()
            await asyncio.sleep(app.indicator_update_timeout)

    async def _check_open_deals(self) -> None:
        for symbol in app.symbol_manager.list():
            if symbol.pause:
                if app.exchange_manager.get('ByBit') in symbol.exchanges:
                    try:
                        symbol.pause = await self._dealer.symbol_has_open_deal(symbol=symbol)
                    except Warning:
                        logger.warning(f'I did not update pause for {symbol}')
                else:
                    symbol.pause = False
