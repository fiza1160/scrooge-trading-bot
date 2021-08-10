from app.exchanges import create_exchange_list


class Symbol:
    def __init__(self, exchanges, base_currency, quote_currency):
        self.exchanges = exchanges
        self.base_currency = base_currency
        self.quote_currency = quote_currency

    def __str__(self):
        return f'{self.base_currency}{self.quote_currency}'

    def __repr__(self):
        return f'{self.base_currency}{self.quote_currency} {self.exchanges}'


def create_symbol_list(*args):
    symbols = []
    unique_symbols = set()

    for arg in args:
        for symbol_info in arg:

            symbol_name = f'{symbol_info["base_currency"]}{symbol_info["quote_currency"]}'
            if symbol_name not in unique_symbols:
                unique_symbols.add(symbol_name)

                symbols.append(
                    Symbol(
                        exchanges=create_exchange_list(symbol_info['exchanges']),
                        base_currency=symbol_info['base_currency'],
                        quote_currency=symbol_info['quote_currency'],
                    )
                )

    return symbols
