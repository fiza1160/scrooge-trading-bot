from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trading_bot import IndicatorManager, IndicatorValueManager, ExchangeManager, SymbolManager, StopLossManager, \
        PauseChecker, AdapterTaAPI, IndicatorUpdater, DecisionMaker, AdapterByBit, Dealer, \
        AdapterTelegram, TradingSystemManager

indicator_manager: IndicatorManager
indicator_value_manager: IndicatorValueManager
exchange_manager: ExchangeManager
symbol_manager: SymbolManager
trading_system_manager: TradingSystemManager
notifier: AdapterTelegram
dealer: Dealer
deals_adapter: AdapterByBit
decision_maker: DecisionMaker
indicator_updater: IndicatorUpdater
indicators_adapter: AdapterTaAPI
pause_checker: PauseChecker
stop_loss_manager: StopLossManager
indicator_update_timeout = 60


def run() -> None:
    asyncio.run(_create_tasks())


async def _create_tasks() -> None:
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
