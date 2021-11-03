from unittest import TestCase

from trading_bot.models.indicators import IndicatorManager, Indicator
from trading_bot.tests.helpers import reset_managers


class TestIndicatorManager(TestCase):

    def setUp(self) -> None:
        reset_managers()

    def test_create(self):
        with self.subTest(case='Try to create create Indicator without optional params'
                               'name should be "Test_1h"'
                               'indicator_type should be "Test"'
                               'interval should be "1h"'
                               'optional should be empty dict'):
            indicator = IndicatorManager().create(
                name='Test_1h',
                indicator_type='Test',
                interval='1h',
            )

            self.assertEqual(indicator.indicator_type, 'Test')
            self.assertEqual(indicator.interval.name, Indicator.Interval('1h').name)
            self.assertEqual(indicator.interval.timeout, Indicator.Interval('1h').timeout)
            self.assertEqual(indicator.optional, {})

        with self.subTest(case='Try to create create Indicator with optional params'
                               'name should be "Test_1h_period10"'
                               'indicator_type should be "Test"'
                               'interval should be "1h"'
                               'period should contain {period: 10}'):
            indicator = IndicatorManager().create(
                name='Test_1h_period10',
                indicator_type='Test',
                interval='1h',
                optional={'optInTimePeriod': 10},
            )

            self.assertEqual(indicator.indicator_type, 'Test')
            self.assertEqual(indicator.interval.name, Indicator.Interval('1h').name)
            self.assertEqual(indicator.interval.timeout, Indicator.Interval('1h').timeout)
            self.assertEqual(indicator.optional, {'optInTimePeriod': 10})

    def test_list(self):
        with self.subTest(case='New and empty IndicatorManager should return empty list'):
            ind_manager = IndicatorManager()

            self.assertEqual(len(ind_manager.list()), 0)

        with self.subTest(case='Try to create indicator '
                               'IndicatorManager should return list with the indicator'):
            ind_manager = IndicatorManager()

            indicator = ind_manager.create(
                name=f'Test_1h',
                indicator_type='Test',
                interval='1h',
            )

            self.assertEqual(len(ind_manager.list()), 1)
            self.assertIn(indicator, ind_manager.list())

        with self.subTest(case='Try to create 10 indicators '
                               'IndicatorManager should return list with 10 indicators'):
            ind_manager = IndicatorManager()
            created_indicators = []

            for n in range(10):
                created_indicators.append(ind_manager.create(
                    name=f'{n}_1h',
                    indicator_type=f'{n}',
                    interval='1h',
                ))

            self.assertEqual(len(ind_manager.list()), 10)
            self.assertEqual(ind_manager.list(), created_indicators)

    def test_get(self):
        with self.subTest(case="If Indicator exists, "
                               "method should return it"):
            ind_manager = IndicatorManager()
            new_indicator = ind_manager.create(
                name='Test_1h',
                indicator_type='Test',
                interval='1h',
            )

            self.assertIs(new_indicator, ind_manager.get(name='Test_1h'))
            self.assertEqual(len(ind_manager.list()), 1)

        with self.subTest(case="If Indicator does not exist, "
                               "method should return None"):
            ind_manager = IndicatorManager()
            ind_manager.create(
                name='Test_1h',
                indicator_type='Test',
                interval='1h',
            )

            self.assertIsNone(ind_manager.get(name='not_exist_name'))
