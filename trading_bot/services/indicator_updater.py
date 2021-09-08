import asyncio
from datetime import datetime, timedelta

from trading_bot import app
from trading_bot.models.indicators import Indicator


class IndicatorUpdater:

    def __init__(
            self,
            indicators_adapter,
            decision_maker,
    ) -> None:
        self._timeout = 60
        self._last_updates = {}
        self._values_updated = False
        self._indicators_adapter = indicators_adapter
        self._decision_maker = decision_maker

    async def run(self) -> None:
        while True:
            self._values_updated = False
            await self._update()
            if self._values_updated:
                self._call_decision_maker()

            await asyncio.sleep(self._timeout)

    async def _update(self) -> None:
        min_timeout = 604800

        indicators = app.indicator_manager.list()
        if not indicators:
            raise ValueError

        for indicator in indicators:
            if indicator.interval.timeout < min_timeout:
                min_timeout = indicator.interval.timeout

            if self._its_time_to_update(indicator):
                await self._update_indicator_values(indicator)
                self._last_updates[indicator] = datetime.now()
                self._values_updated = True

        self._timeout = min_timeout

    def _its_time_to_update(self, indicator: Indicator) -> bool:
        its_time = False

        last_update_time = self._last_updates.get(indicator)
        if not last_update_time:
            its_time = True
        elif (last_update_time + timedelta(seconds=indicator.interval.timeout)) <= datetime.now():
            its_time = True

        return its_time

    async def _update_indicator_values(self, indicator: Indicator) -> None:
        symbols = app.symbol_manager.list()
        if not symbols:
            raise ValueError

        for symbol in symbols:
            if not symbol.pause:
                new_values = await self._indicators_adapter.get_indicator_values(
                    symbol=symbol,
                    indicator=indicator
                )
                if new_values:
                    app.indicator_value_manager.update(
                        symbol=symbol,
                        indicator=indicator,
                        present_value=new_values['present_value'],
                        previous_value=new_values['previous_value']
                    )

    def _call_decision_maker(self) -> None:
        self._decision_maker.decide()