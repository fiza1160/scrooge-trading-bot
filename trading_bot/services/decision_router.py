from trading_bot.models.exchanges import DealOpeningMethod
from trading_bot.services.deal_opener import DealOpener
from trading_bot.services.notifier import Notifier


class DecisionRouter:

    def __init__(self,
                 notifier: Notifier,
                 deal_opener: DealOpener):
        self.notifier = notifier
        self.deal_opener = deal_opener

    async def rout(self, decision) -> None:
        for exchange in decision.symbol.exchanges:
            if exchange.deal_opening_method == DealOpeningMethod.SEND_MESSAGE:
                await self.notifier.notify(msg=str(decision))
            elif exchange.deal_opening_method == DealOpeningMethod.OPEN_DEAL:
                await self.deal_opener.open_deal(decision)
