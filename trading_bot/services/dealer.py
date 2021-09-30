import logging

from trading_bot import app
from trading_bot.models.symbols import Symbol
from trading_bot.services.decision_maker import DealSide

logger = logging.getLogger('logger')


class Deal:
    def __init__(
            self,
            symbol: Symbol,
            side: DealSide,
            size: float,
            entry_price: float,
            stop_loss: float,
            take_profit: float,
    ):
        self.symbol = symbol
        self.side = side
        self.size = size
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit


class Dealer:
    def __init__(self, deals_adapter):
        self._deals_adapter = deals_adapter

    async def open_deal(self, decision):
        current_price = await self._deals_adapter.get_current_price(
            symbol=decision.symbol,
        )

        stop_loss = self._count_stop_loss_value(decision.side, current_price)

        await self._deals_adapter.create_order(
            side=decision.side,
            symbol=decision.symbol,
            stop_loss=stop_loss,
        )

        msg = f'I just opened a deal (ByBit). ({decision})'
        logger.info(msg)
        await app.notifier.notify(msg=msg)

    @staticmethod
    def _count_stop_loss_value(
            side: DealSide,
            entry_price: float
    ):
        sl_percent = 0.02
        if side is DealSide.BUY:
            sl_price = entry_price * (1 - sl_percent)
        else:
            sl_price = entry_price * (1 + sl_percent)

        return round(sl_price, 2)

    async def symbol_has_open_deal(self, symbol):
        response = await self._deals_adapter.get_positions_by_symbol(symbol)

        has_open_deals = False
        for res in response.get('result'):
            if res['size'] != 0:
                has_open_deals = True

        return has_open_deals

    async def get_deals_by_symbol(self, symbol):
        response = await self._deals_adapter.get_positions_by_symbol(symbol)

        deals = []
        for res in response.get('result'):
            if res['size'] != 0:
                deals.append(
                    Deal(
                        symbol=app.symbol_manager.find_by_alias(
                            alias=res['symbol'],
                            alias_template=self._deals_adapter.symbol_template,
                        ),
                        side=DealSide[res['side'].upper()],
                        size=res['size'],
                        entry_price=res['entry_price'],
                        stop_loss=res['stop_loss'],
                        take_profit=res['take_profit'],
                    )
                )

        return deals

    async def set_stop_loss(self, deal, stop_loss):
        await self._deals_adapter.set_stop_loss(deal, stop_loss)
