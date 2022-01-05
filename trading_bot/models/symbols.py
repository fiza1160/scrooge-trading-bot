from typing import List, Dict, Union

from trading_bot.models.exchanges import Exchange


class Symbol:
    class DealOpeningParams:
        def __init__(
                self,
                qty: float,
        ) -> None:
            self.qty = qty

    def __init__(
            self,
            base_currency: str,
            quote_currency: str,
            exchanges: List[Exchange],
            deal_opening_params: Dict[str, float],
    ) -> None:
        self.name = f'{base_currency}{quote_currency}'
        self.exchanges = exchanges
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.deal_opening_params = self._create_deal_opening_params(deal_opening_params)
        self.pause = False

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.name} {self.exchanges} is paused: {self.pause}'

    def _create_deal_opening_params(self, deal_opening_params):
        return self.DealOpeningParams(qty=deal_opening_params.get('qty'))


class SymbolManager:
    def __init__(self) -> None:
        self._symbols = []

    def create(
            self,
            base_currency: str,
            quote_currency: str,
            exchanges: List[Exchange],
            deal_opening_params: Dict[str, float],
    ) -> Symbol:
        symbol = Symbol(
            base_currency=base_currency,
            quote_currency=quote_currency,
            exchanges=exchanges,
            deal_opening_params=deal_opening_params,
        )

        self._symbols.append(symbol)

        return symbol

    def list(self) -> List[Symbol]:
        return self._symbols.copy()

    def find_by_alias(self, alias: str, alias_template: str) -> Union[Symbol, None]:
        for symbol in self.list():
            if alias_template.format(
                    base_currency=symbol.base_currency,
                    quote_currency=symbol.quote_currency,
            ) == alias:
                return symbol
        return None
