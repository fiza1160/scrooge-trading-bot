from app.exchanges import DealOpeningMethod

SEND_MESSAGE = DealOpeningMethod.SEND_MESSAGE
OPEN_DEAL = DealOpeningMethod.OPEN_DEAL


class DealOpeningRouter:

    @staticmethod
    async def route_deal(decision_queue, message_queue, deal_queue):
        while True:
            decision = await decision_queue.get()

            for exchange in decision.symbol.exchanges:
                if exchange.deal_opening_method == SEND_MESSAGE:
                    await message_queue.put(str(decision))
                elif exchange.deal_opening_method == OPEN_DEAL:
                    await deal_queue.put(decision)
                else:
                    # TODO add logger
                    print(f'DealOpeningMethod {exchange.deal_opening_method} is not implemented')

            decision_queue.task_done()
