import asyncio

indicator_manager = None
indicator_value_manager = None
exchange_manager = None
symbol_manager = None
trading_system_manager = None
notifier = None
dealer = None
deals_adapter = None
decision_router = None
decision_maker = None
indicator_updater = None
indicator_informer = None
indicators_adapter = None
pause_checker = None
stop_loss_manager = None
indicator_update_timeout = 60


def run() -> None:
    asyncio.run(_create_tasks())


async def _create_tasks():
    task_indicator_updater = asyncio.create_task(
        indicator_updater.run(),
        name='Indicator Updater'
    )

    task_pause_checker = asyncio.create_task(
        pause_checker.run(),
        name='Pause Checker'
    )

    task_stop_loss_manager = asyncio.create_task(
        stop_loss_manager.run(),
        name='Stop Loss Manager'
    )

    await asyncio.gather(
        task_indicator_updater,
        task_pause_checker,
        task_stop_loss_manager,
    )
