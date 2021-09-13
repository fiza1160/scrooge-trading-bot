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
        self._last_updates = {}
        self._values_updated = False
        self._indicators_adapter = indicators_adapter
        self._decision_maker = decision_maker

    async def run(self) -> None:
        while True:
            # TODO add logger
            msg = f'I started to update the values of the indicators.'
            print(msg)

            self._values_updated = False
            await self._update()
            if self._values_updated:
                await self._call_decision_maker()

            # TODO add logger
            msg = f'I just updated indicator values. ' \
                  f'Next update at {datetime.now() + timedelta(seconds=app.indicator_update_timeout)}'
            print(msg)

            await asyncio.sleep(app.indicator_update_timeout)

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

        app.indicator_update_timeout = min_timeout / 2

    def _its_time_to_update(self, indicator: Indicator) -> bool:
        its_time = False

        last_update_time = self._last_updates.get(indicator)
        if not last_update_time:
            its_time = True
        elif (last_update_time + timedelta(seconds=(indicator.interval.timeout / 2))) <= datetime.now():
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

    async def _call_decision_maker(self) -> None:
        await self._decision_maker.decide()
