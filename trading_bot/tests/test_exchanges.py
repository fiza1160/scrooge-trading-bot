from unittest import TestCase

from trading_bot.models.exchanges import ExchangeManager, DealOpeningMethod
from trading_bot.tests.helpers import reset_managers


class TestExchangeManager(TestCase):

    def setUp(self) -> None:
        reset_managers()

    def test_create(self):
        ex_manager = ExchangeManager()

        with self.subTest(case='Try to create Exchange with deal_opening_method = "send_message" '
                               'deal_opening_method should be DealOpeningMethod.SEND_MESSAGE'):
            exchange = ex_manager.create(name='Test_Send_Message', deal_opening_method='send_message')

            self.assertEqual(exchange.name, 'Test_Send_Message')
            self.assertEqual(exchange.deal_opening_method, DealOpeningMethod.SEND_MESSAGE)

        with self.subTest(case='Try to create Exchange with deal_opening_method = "open_deal" '
                               'deal_opening_method should be DealOpeningMethod.OPEN_DEAL'):
            exchange = ex_manager.create(name='Test_Open_Deal', deal_opening_method='open_deal')

            self.assertEqual(exchange.name, 'Test_Open_Deal')
            self.assertEqual(exchange.deal_opening_method, DealOpeningMethod.OPEN_DEAL)

        with self.subTest(case='Try to create Exchange with deal_opening_method = "another_method" '
                               'ValueError exception must be raised'):
            with self.assertRaises(ValueError):
                ex_manager.create(name='Test_Another_Method', deal_opening_method='another_method')

    def test_list(self):
        with self.subTest(case='New and empty ExchangeManager should return empty list'):
            ex_manager = ExchangeManager()
            self.assertEqual(len(ex_manager.list()), 0)

        with self.subTest(case='Try to create exchange '
                               'ExchangeManager should return list with the exchange'):

            ex_manager = ExchangeManager()
            new_exchange = ex_manager.create(name='1', deal_opening_method='send_message')

            self.assertEqual(len(ex_manager.list()), 1)
            self.assertIn(new_exchange, ex_manager.list())

        with self.subTest(case='Try to create 10 exchanges '
                               'ExchangeManager should return list with 10 exchanges'):
            ex_manager = ExchangeManager()
            created_exchanges = []

            for n in range(10):
                created_exchanges.append(ex_manager.create(name=f'{n}', deal_opening_method='send_message'))

            self.assertEqual(len(ex_manager.list()), 10)
            self.assertEqual(created_exchanges, ex_manager.list())

    def test_get(self):
        ex_manager = ExchangeManager()
        ex_manager.create(name='StormGain', deal_opening_method='send_message')
        ex_manager.create(name='ByBit', deal_opening_method='open_deal')

        with self.subTest(case='Try to get "StormGain". ExchangeManager should return Exchange. '
                               'Exchange name should be "StormGain" '
                               'and deal_opening_method should be DealOpeningMethod.SEND_MESSAGE'):
            exchange = ex_manager.get(name='StormGain')

            self.assertEqual(exchange.name, 'StormGain')
            self.assertEqual(exchange.deal_opening_method, DealOpeningMethod.SEND_MESSAGE)

        with self.subTest(case='Try to get "ByBit". ExchangeManager should return Exchange. '
                               'Exchange name should be "ByBit" '
                               'and deal_opening_method should be DealOpeningMethod.OPEN_DEAL'):
            exchange = ex_manager.get(name='ByBit')

            self.assertEqual(exchange.name, 'ByBit')
            self.assertEqual(exchange.deal_opening_method, DealOpeningMethod.OPEN_DEAL)
