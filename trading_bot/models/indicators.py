from typing import Dict, List


class Indicator:
    class Interval:
        valid_values = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '30m': 1800,
            '1h': 3600,
            '2h': 7200,
            '4h': 14400,
            '12h': 43200,
            '1d': 86400,
            '1w': 604800,
        }

        def __init__(self, name: str) -> None:
            self.name = name
            self.timeout = self.valid_values.get(name)

    def __init__(
            self,
            name: str,
            indicator_type: str,
            interval: Interval,
            optional: Dict[str, str] = None,
    ) -> None:
        self.name = name
        self.indicator_type = indicator_type
        self.interval = interval
        self.optional = optional or {}

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class IndicatorManager:

    def __init__(self) -> None:
        self._indicators = []
        self._indicators_by_name = {}

    def create(
            self,
            name: str,
            indicator_type: str,
            interval: str,
            optional: Dict[str, str] = None,
    ) -> Indicator:
        indicator = Indicator(
            name=name,
            indicator_type=indicator_type,
            interval=Indicator.Interval(name=interval),
            optional=optional,
        )

        self._indicators.append(indicator)
        self._indicators_by_name[indicator.name] = indicator

        return indicator

    def list(self) -> List[Indicator]:
        return self._indicators.copy()

    def get(self, name: str) -> Indicator:
        return self._indicators_by_name.get(name)
