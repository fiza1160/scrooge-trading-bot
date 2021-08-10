import asyncio


class App:

    def __init__(
            self,
            rsi_checker,
            decision_maker,
            deal_opener,
            notifier,
    ):
        self.rsi_checker = rsi_checker
        self.decision_maker = decision_maker
        self.deal_opener = deal_opener
        self.notifier = notifier

    def run(self) -> None:
        asyncio.run(self._create_tasks())

    async def _create_tasks(self):
        rsi_queue = asyncio.Queue()
        decision_queue = asyncio.Queue()
        message_queue = asyncio.Queue()
        order_queue = asyncio.Queue()

        task_rsi_checker = asyncio.create_task(self.rsi_checker.check(rsi_queue), name='RSI Checker')
        task_decision_maker = asyncio.create_task(self.decision_maker.choose_rising_low_rsi(rsi_queue, decision_queue),
                                                  name='Decision Maker')
        task_deal_opener = asyncio.create_task(self.deal_opener.open_deal(decision_queue, message_queue, order_queue),
                                               name='Deal Opener')
        task_notifier = asyncio.create_task(self.notifier.notify(message_queue), name='Notifier')

        await asyncio.gather(
            task_rsi_checker,
            task_decision_maker,
            task_deal_opener,
            task_notifier,
        )
