import asyncio
from enum import Enum, auto


class Side(Enum):
    Buy = auto()
    Sell = auto()


class Decision:
    def __init__(self, symbol, side, cause):
        self.symbol = symbol
        self.side = side
        self.cause = cause

    def __str__(self):
        return f'Need to {self.side.name} {self.symbol} ({self.cause})'

    def __repr__(self):
        return f'{self.symbol}, {self.side} ({self.cause})'


class DecisionMaker:

    @staticmethod
    async def choose_rising_low_rsi(rsi_queue: asyncio.Queue,
                                    decision_queue: asyncio.Queue) -> None:
        while True:
            rsi_info = await rsi_queue.get()
            if rsi_info.present_value > rsi_info.previous_value < 30:
                await decision_queue.put(
                    Decision(
                        symbol=rsi_info.symbol,
                        side=Side.Buy,
                        cause=str(rsi_info)
                    )
                )

            rsi_queue.task_done()
