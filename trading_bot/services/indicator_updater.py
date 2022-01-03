import asyncio
from datetime import datetime, timedelta
import logging

from trading_bot import app, IndicatorInformer, DecisionMaker
from trading_bot.models.indicators import Indicator

logger = logging.getLogger('logger')


class IndicatorUpdater:

    def __init__(
            self,
            indicator_informer: IndicatorInformer,
            decision_maker: DecisionMaker,
    ) -> None:
        self._last_updates = {}
        self._values_updated = False
        self._indicator_informer = indicator_informer
        self._decision_maker = decision_maker

    async def run(self) -> None:
        while True:
            logger.info(f'I started to update indicator values.')

            self._values_updated = False
            await self._update()
            if self._values_updated:
                await self._call_decision_maker()

            logger.info(f'I just updated indicator values. '
                        f'Next update at {datetime.now() + timedelta(seconds=app.indicator_update_timeout)}')

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
                try:
                    new_values = await self._indicator_informer.get_indicator_values(
                        symbol=symbol,
                        indicator=indicator
                    )
                except Warning:
                    logger.warning(f'I did not get the new indicator values for {symbol}')
                    continue

                app.indicator_value_manager.update(
                    symbol=symbol,
                    indicator=indicator,
                    present_value=new_values['present_value'],
                    previous_value=new_values['previous_value']
                )

    async def _call_decision_maker(self) -> None:
        await self._decision_maker.decide()
