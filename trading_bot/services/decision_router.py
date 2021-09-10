from trading_bot.models.exchanges import DealOpeningMethod


class DecisionRouter:

    def __init__(self,
                 notifier,
                 dealer):
        self._notifier = notifier
        self._dealer = dealer

    async def rout(self, decision) -> None:
        for exchange in decision.symbol.exchanges:
            if exchange.deal_opening_method == DealOpeningMethod.SEND_MESSAGE:
                await self._notifier.notify(msg=str(decision))
            elif exchange.deal_opening_method == DealOpeningMethod.OPEN_DEAL:
                await self._dealer.open_deal(decision)
