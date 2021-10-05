import asyncio
import logging

from trading_bot import app
from trading_bot.models.symbols import Symbol
from trading_bot.services.dealer import Deal
from trading_bot.services.decision_maker import DealSide

logger = logging.getLogger('logger')


class StopLossManager:

    def __init__(
            self,
    ) -> None:
        self._stop_loss_indicator = app.indicator_manager.create(
            name='ParabolicSAR_1h',
            indicator_type='ParabolicSAR',
            interval='1h',
        )

    async def run(self) -> None:
        while True:
            await self._update_stop_losses()
            await asyncio.sleep(app.indicator_update_timeout)

    async def _update_stop_losses(self) -> None:
        symbols = self._get_symbols_with_open_deals()
        for symbol in symbols:
            deals = await app.dealer.get_deals_by_symbol(symbol)
            current_price = await app.dealer.get_current_price(symbol=symbol)
            for deal in deals:
                stop_loss = await self._get_new_stop_loss_value(deal=deal, current_price=current_price)
                await app.dealer.set_stop_loss(deal, stop_loss)

                logger.info(f'I just updated stop loss for {deal.symbol}')

    @staticmethod
    def _get_symbols_with_open_deals() -> [Symbol]:
        symbols_with_deals = []

        for symbol in app.symbol_manager.list():
            if symbol.pause:
                symbols_with_deals.append(symbol)

        return symbols_with_deals

    async def _get_new_stop_loss_value(
            self,
            deal: Deal,
            current_price: float,
    ) -> float:

        indicator_value = await app.indicators_adapter.get_indicator_values(
            symbol=deal.symbol,
            indicator=self._stop_loss_indicator,
        )
        indicator_value = indicator_value['present_value']

        current_stop_loss = deal.stop_loss

        if deal.side == DealSide.BUY:
            new_sl = indicator_value if current_price > indicator_value > current_stop_loss else current_stop_loss
        else:
            new_sl = indicator_value if current_price < indicator_value < current_stop_loss else current_stop_loss

        return new_sl
