import asyncio

indicator_manager = None
indicator_value_manager = None
exchange_manager = None
symbol_manager = None
trading_system_manager = None
notifier = None
deal_opener = None
decision_router = None
decision_maker = None
indicator_updater = None
indicators_adapter = None


def run() -> None:
    asyncio.run(_create_tasks())


async def _create_tasks():
    task_indicator_updater = asyncio.create_task(
        indicator_updater.run(),
        name='Indicator Updater'
    )

    await asyncio.gather(
        task_indicator_updater,
    )
