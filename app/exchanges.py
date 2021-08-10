from abc import ABC, abstractmethod
from enum import Enum, auto
from functools import cache


class DealOpeningMethod(Enum):
    CREATE_ORDER = auto()
    SEND_MESSAGE = auto()


class Exchange(ABC):

    @property
    @abstractmethod
    def deal_opening_method(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class StormGain(Exchange):

    @property
    def name(self):
        return 'StormGain'

    @property
    def deal_opening_method(self):
        return DealOpeningMethod.SEND_MESSAGE


class ByBit(Exchange):

    @property
    def name(self):
        return 'ByBit'

    @property
    def deal_opening_method(self):
        return DealOpeningMethod.CREATE_ORDER


def create_exchange_list(exchanges):
    exchange_list = []

    for exchange_name in exchanges:
        exchange_list.append(_create_exchange_by_name(exchange_name))

    return exchange_list


@cache
def _create_exchange_by_name(exchange_name):
    if exchange_name == 'stormgain':
        exchange = StormGain()
    elif exchange_name == 'bybit':
        exchange = ByBit()
    else:
        raise ValueError

    return exchange
