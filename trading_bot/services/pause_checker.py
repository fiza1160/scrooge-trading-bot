from trading_bot import app


class PauseChecker:
    def __init__(self, dealer):
        self._dealer = dealer

    async def run(self):
        while True:
            await self._check_open_deals()
            await asyncio.sleep(app.indicator_update_timeout)

    async def _check_open_deals(self):
        for symbol in app.symbol_manager.list():
            if symbol.pause:
                symbol.pause = await self._dealer.symbol_has_open_deal(symbol=symbol)


