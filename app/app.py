import asyncio


class App:

    def __init__(self, rsi_checker, decision_maker, notifier):
        self.rsi_checker = rsi_checker
        self.decision_maker = decision_maker
        self.notifier = notifier

    def run(self) -> None:
        asyncio.run(self._create_tasks())

    async def _create_tasks(self):
        rsi_queue = asyncio.Queue()
        decision_queue = asyncio.Queue()

        rsi_checker_task = asyncio.create_task(self.rsi_checker.check(rsi_queue), name='RSI Checker')
        decision_maker_task = asyncio.create_task(self.decision_maker.choose_rising_low_rsi(rsi_queue, decision_queue),
                                             name='Decision Maker')
        notifier_task = asyncio.create_task(self.notifier.notify(decision_queue), name='Notifier')

        await asyncio.gather(
            rsi_checker_task,
            decision_maker_task,
            notifier_task,
        )
