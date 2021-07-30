import asyncio


class QueuePrinter:
    @staticmethod
    async def print(queue: asyncio.Queue) -> None:
        while True:
            task = await queue.get()
            print(task)
            queue.task_done()