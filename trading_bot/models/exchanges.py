from enum import Enum, auto
from typing import List


class DealOpeningMethod(Enum):
    OPEN_DEAL = auto()
    SEND_MESSAGE = auto()


class Exchange:

    def __init__(self, name: str, deal_opening_method: DealOpeningMethod) -> None:
        self.name = name
        self.deal_opening_method = deal_opening_method

    def __str__(self) -> str:
        return f'{self.name}, {self.deal_opening_method}'

    def __repr__(self) -> str:
        return f'{self.name}, {self.deal_opening_method}'


class ExchangeManager:

    def __init__(self) -> None:
        self._exchanges = []
        self._exchanges_by_name = {}

    def create(self, name: str, deal_opening_method: str) -> Exchange:
        exchange = Exchange(
            name=name,
            deal_opening_method=self._get_deal_opening_method_by_name(deal_opening_method),
        )
        self._exchanges.append(exchange)
        self._exchanges_by_name[name.upper()] = exchange

        return exchange

    def list(self) -> List[Exchange]:
        return self._exchanges.copy()

    def get(self, name: str) -> Exchange:
        return self._exchanges_by_name.get(name.upper())

    @staticmethod
    def _get_deal_opening_method_by_name(deal_opening_method_name: str) -> DealOpeningMethod:
        if deal_opening_method_name == 'open_deal':
            deal_opening_method = DealOpeningMethod.OPEN_DEAL
        elif deal_opening_method_name == 'send_message':
            deal_opening_method = DealOpeningMethod.SEND_MESSAGE
        else:
            raise ValueError

        return deal_opening_method
