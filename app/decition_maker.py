import asyncio


class DecisionMaker:

    @staticmethod
    async def choose_rising_low_rsi(rsi_queue: asyncio.Queue,
                                    decision_queue: asyncio.Queue) -> None:
        while True:
            rsi = await rsi_queue.get()
            if rsi.present_value > rsi.previous_value < 30:
                await decision_queue.put(str(rsi))

            rsi_queue.task_done()
