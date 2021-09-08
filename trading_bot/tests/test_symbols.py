from unittest import TestCase

from trading_bot import app
from trading_bot.models.symbols import SymbolManager
from trading_bot.tests.helpers import reset_managers


class TestSymbolManager(TestCase):

    def setUp(self) -> None:
        reset_managers()

    def test_create(self):
        sym_manager = SymbolManager()

        test_exchange = app.exchange_manager.create(name='TestExchange', deal_opening_method='send_message')
        bybit = app.exchange_manager.create(name='ByBit', deal_opening_method='open_deal')
        stormgain = app.exchange_manager.create(name='StormGain', deal_opening_method='send_message')

        with self.subTest(case='Try to create Symbol '
                               'base_currency should be BTC'
                               'quote_currency should be USDT'
                               'exchanges should be ["TestExchange"]'
                               'deal_opening_params should be qty=0.003'
                               'pause should be False'):

            symbol = sym_manager.create(
                base_currency='BTC',
                quote_currency='USDT',
                exchanges=[test_exchange],
                deal_opening_params={'qty': 0.003}
            )

            self.assertEqual(symbol.base_currency, 'BTC')
            self.assertEqual(symbol.quote_currency, 'USDT')
            self.assertIn(test_exchange, symbol.exchanges)
            self.assertEqual(symbol.deal_opening_params.qty, 0.003)
            self.assertEqual(symbol.pause, False)

        with self.subTest(case='Try to create create Symbol with only ByBit exchange '
                               'exchanges should be ["ByBit"]'):

            symbol = sym_manager.create(
                base_currency='BTC',
                quote_currency='USDT',
                exchanges=[bybit],
                deal_opening_params={'qty': 0.003}
            )

            self.assertIn(bybit, symbol.exchanges)

        with self.subTest(case='Try to create create Symbol with only StormGain exchange '
                               'exchanges should be ["StormGain"]'):
            symbol = sym_manager.create(
                base_currency='BTC',
                quote_currency='USDT',
                exchanges=[stormgain],
                deal_opening_params={'qty': 0.003}
            )

            self.assertIn(stormgain, symbol.exchanges)

        with self.subTest(case='Try to create create Symbol with ByBit and StormGain exchanges '
                               'exchanges should be ["StormGain", "ByBit"]'):
            symbol = sym_manager.create(
                base_currency='BTC',
                quote_currency='USDT',
                exchanges=[bybit, stormgain],
                deal_opening_params={'qty': 0.003}
            )

            self.assertIn(bybit, symbol.exchanges)
            self.assertIn(stormgain, symbol.exchanges)

    def test_list(self):
        test_exchange = app.exchange_manager.create(name='TestExchange', deal_opening_method='send_message')

        with self.subTest(case='New and empty SymbolManager should return empty list'):
            sym_manager = SymbolManager()
            self.assertEqual(len(sym_manager.list()), 0)

        with self.subTest(case='Try to create symbol '
                               'SymbolManager should return list with the symbol'):
            sym_manager = SymbolManager()
            new_symbol = sym_manager.create(
                base_currency='1',
                quote_currency='Test',
                exchanges=[test_exchange],
                deal_opening_params={'qty': 0.003}
            )

            self.assertEqual(len(sym_manager.list()), 1)
            self.assertIn(new_symbol, sym_manager.list())

        with self.subTest(case='Try to create 10 symbols '
                               'SymbolManager should return list with 10 symbols'):
            sym_manager = SymbolManager()
            created_symbols = []

            for n in range(10):
                created_symbols.append(sym_manager.create(
                    base_currency=f'{n}',
                    quote_currency='Test',
                    exchanges=[test_exchange],
                    deal_opening_params={'qty': 0.003}
                ))

            self.assertEqual(len(sym_manager.list()), 10)
            self.assertEqual(created_symbols, sym_manager.list())
