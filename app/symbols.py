class Symbol:
    def __init__(self, exchanges, base_currency, quote_currency):
        self.exchanges = exchanges
        self.base_currency = base_currency
        self.quote_currency = quote_currency

    def __str__(self):
        return f'{self.base_currency}{self.quote_currency}'


def create_symbols_list(*args):
    all_symbols_list = []
    unique_symbols = set()

    for symbol_list in args:
        for symbol in symbol_list:
            symbol_name = f'{symbol["base_currency"]}{symbol["quote_currency"]}'
            if symbol_name not in unique_symbols:
                unique_symbols.add(symbol_name)

                all_symbols_list.append(Symbol(
                        exchanges=symbol['exchanges'],
                        base_currency=symbol['base_currency'],
                        quote_currency=symbol['quote_currency'],
                    ))

    return all_symbols_list

