from app.exchanges import DealOpeningMethod

SEND_MESSAGE = DealOpeningMethod.SEND_MESSAGE
CREATE_ORDER = DealOpeningMethod.CREATE_ORDER


class DealOpener:

    @staticmethod
    async def open_deal(decision_queue, message_queue, order_queue):
        while True:
            decision = await decision_queue.get()

            for exchange in decision.symbol.exchanges:
                if exchange.deal_opening_method == SEND_MESSAGE:
                    await message_queue.put(str(decision))
                elif exchange.deal_opening_method == CREATE_ORDER:
                    await order_queue.put(decision)
                else:
                    # TODO add logger
                    print(f'DealOpeningMethod {exchange.deal_opening_method} is not implemented')

            decision_queue.task_done()
