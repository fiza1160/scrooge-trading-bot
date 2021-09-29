from trading_bot.models.exchanges import Exchange


class Symbol:
    class DealOpeningParams:
        def __init__(
                self,
                qty: float,
        ):
            self.qty = qty

    def __init__(
            self,
            base_currency: str,
            quote_currency: str,
            exchanges: [Exchange],
            deal_opening_params: {},
    ):
        self.name = f'{base_currency}{quote_currency}'
        self.exchanges = exchanges
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.deal_opening_params = self._create_deal_opening_params(deal_opening_params)
        self.pause = False

    def __str__(self):
        return self.name

    def __repr__(self):
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
            exchanges: [Exchange],
            deal_opening_params: {},
    ) -> Symbol:
        symbol = Symbol(
            base_currency=base_currency,
            quote_currency=quote_currency,
            exchanges=exchanges,
            deal_opening_params=deal_opening_params,
        )

        self._symbols.append(symbol)

        return symbol

    def list(self) -> [Symbol]:
        return self._symbols.copy()

    def find_by_alias(self, alias: str, alias_template: str) -> Symbol or None:
        for symbol in self.list():
            if alias_template.format(
                    base_currency=symbol.base_currency,
                    quote_currency=symbol.quote_currency,
            ) == alias:
                return symbol
        return None
