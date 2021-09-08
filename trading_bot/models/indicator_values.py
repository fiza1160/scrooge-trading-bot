from datetime import datetime, timedelta

from trading_bot.models.indicators import Indicator
from trading_bot.models.symbols import Symbol


class IndicatorValue:
    def __init__(
            self,
            indicator: Indicator,
            symbol: Symbol,
            present_value: float,
            previous_value: float,
            updated_at: datetime
    ) -> None:
        self.indicator = indicator
        self.symbol = symbol
        self.present_value = present_value
        self.previous_value = previous_value
        self.updated_at = updated_at

    def __str__(self) -> str:
        return f'{self.indicator} {self.symbol} present_value: ' \
               f'{self.present_value} previous_value: {self.previous_value}'

    def __repr__(self) -> str:
        return f'{self.indicator} {self.symbol} present_value: ' \
               f'{self.present_value} previous_value: {self.previous_value}'

    def is_actual(self) -> bool:
        return self.updated_at + timedelta(seconds=self.indicator.interval.timeout) > datetime.now()


class IndicatorValueManager:
    def __init__(self) -> None:
        self._indicator_values = []
        self._indicator_values_by_key = {}

    def get(
            self,
            indicator: Indicator,
            symbol: Symbol,
    ) -> IndicatorValue:
        return self._indicator_values_by_key.get(self._key(indicator, symbol))

    def update(
            self,
            indicator: Indicator,
            symbol: Symbol,
            present_value: float,
            previous_value: float,
    ) -> IndicatorValue:
        ind_value = self.get(indicator, symbol)

        if ind_value:
            ind_value.present_value = present_value
            ind_value.previous_value = previous_value
            ind_value.updated_at = datetime.now()
        else:
            ind_value = self.create(
                indicator=indicator,
                symbol=symbol,
                present_value=present_value,
                previous_value=previous_value,
            )

        return ind_value

    def create(
            self,
            indicator: Indicator,
            symbol: Symbol,
            present_value: float,
            previous_value: float,
    ) -> IndicatorValue:
        indicator_value = IndicatorValue(
            indicator=indicator,
            symbol=symbol,
            present_value=present_value,
            previous_value=previous_value,
            updated_at=datetime.now()
        )

        self._indicator_values_by_key[self._key(indicator, symbol)] = indicator_value
        self._indicator_values.append(indicator_value)

        return indicator_value

    def list(self) -> [IndicatorValue]:
        return self._indicator_values.copy()

    @staticmethod
    def _key(indicator: Indicator, symbol: Symbol):
        return f'{indicator.name}_{symbol.name}'
