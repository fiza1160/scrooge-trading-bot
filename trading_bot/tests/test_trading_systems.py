import copy
import json
import os
from unittest import TestCase

from trading_bot import app
from trading_bot.models.trading_systems import TradingSystemManager, TradingSystemSettingsValidator, Condition
from trading_bot.tests.helpers import reset_managers

base_dir = os.path.abspath(os.path.dirname(__file__))
settings_dir = f'{base_dir}\\static'


class TradingSystemSettingsLoader:

    @staticmethod
    def correct_settings():
        with open(f'{settings_dir}\\trading_system_settings_correct.json') as f:
            return json.load(f)


class TestTradingSystemManager(TestCase):

    def setUp(self) -> None:
        reset_managers()

    def test_create(self):
        with self.subTest(case='Try to create create TradingSystem '
                               'indicators should be [10_Momentum_1h, 4_MovingAverage_1h, 9_MovingAverage_1h]'
                               'exchanges should be [ByBit, StormGain]'
                               'conditions_to_buy should be '
                               'conditions_to_sell should be '):
            settings = TradingSystemSettingsLoader.correct_settings()

            test_indicators = self._create_indicators()
            test_exchanges = self._create_exchanges()
            test_conditions_to_buy = self._create_conditions_to_buy()
            test_conditions_to_sell = self._create_conditions_to_sell()
            test_uptrend_conditions = self._create_uptrend_conditions()
            test_downtrend_conditions = self._create_downtrend_conditions()

            ts_manager = TradingSystemManager(
                indicator_manager=app.indicator_manager,
                exchange_manager=app.exchange_manager,
            )
            trading_system = ts_manager.create(
                name=settings[0].get('name'),
                settings=settings[0].get('settings')
            )

            self.assertEqual(trading_system.indicators, test_indicators)
            self.assertEqual(trading_system.exchanges, test_exchanges)

            self._assert_conditions(test_conditions_to_buy, trading_system.conditions_to_buy)
            self._assert_conditions(test_conditions_to_sell, trading_system.conditions_to_sell)
            self._assert_conditions(test_uptrend_conditions, trading_system.uptrend_conditions)
            self._assert_conditions(test_downtrend_conditions, trading_system.downtrend_conditions)

    @staticmethod
    def _create_indicators():
        ind_manager = app.indicator_manager
        indicators = [
            ind_manager.create(name='10_Momentum_1w', period=10, indicator_type='Momentum', interval='1w'),
            ind_manager.create(name='4_MovingAverage_4h', period=4, indicator_type='MovingAverage', interval='4h'),
            ind_manager.create(name='9_MovingAverage_4h', period=10, indicator_type='Momentum', interval='4h'),
            ind_manager.create(name='4_MovingAverage_1w', period=4, indicator_type='MovingAverage', interval='1w'),
            ind_manager.create(name='9_MovingAverage_1w', period=9, indicator_type='MovingAverage', interval='1w')
        ]
        return indicators

    @staticmethod
    def _create_exchanges():
        return [
            app.exchange_manager.create(name='ByBit', deal_opening_method='open_deal'),
            app.exchange_manager.create(name='StormGain', deal_opening_method='send_message'),
        ]

    @staticmethod
    def _create_conditions_to_buy():
        type_indicator = Condition.Operand.OperandType.INDICATOR_VALUE
        return [
            Condition(
                first_operand=Condition.Operand(operand_type=type_indicator,
                                                comparison_value='4_MovingAverage_4h.present_value'),
                operator='>',
                second_operand=Condition.Operand(operand_type=type_indicator,
                                                 comparison_value='9_MovingAverage_4h.present_value'),
            ),
        ]

    @staticmethod
    def _create_conditions_to_sell():
        type_indicator = Condition.Operand.OperandType.INDICATOR_VALUE
        return [
            Condition(
                first_operand=Condition.Operand(operand_type=type_indicator,
                                                comparison_value='9_MovingAverage_4h.present_value'),
                operator='>',
                second_operand=Condition.Operand(operand_type=type_indicator,
                                                 comparison_value='4_MovingAverage_4h.present_value'),
            ),
        ]

    @staticmethod
    def _create_uptrend_conditions():
        type_indicator = Condition.Operand.OperandType.INDICATOR_VALUE
        return [
            Condition(
                first_operand=Condition.Operand(operand_type=type_indicator,
                                                comparison_value='10_Momentum_1w.present_value'),
                operator='>',
                second_operand=Condition.Operand(operand_type=type_indicator,
                                                 comparison_value='10_Momentum_1w.previous_value'),
            ),
            Condition(
                first_operand=Condition.Operand(operand_type=type_indicator,
                                                comparison_value='9_MovingAverage_1w.present_value'),
                operator='<',
                second_operand=Condition.Operand(operand_type=type_indicator,
                                                 comparison_value='4_MovingAverage_1w.present_value'),
            ),
        ]

    @staticmethod
    def _create_downtrend_conditions():
        type_indicator = Condition.Operand.OperandType.INDICATOR_VALUE
        return [
            Condition(
                first_operand=Condition.Operand(operand_type=type_indicator,
                                                comparison_value='10_Momentum_1w.present_value'),
                operator='<',
                second_operand=Condition.Operand(operand_type=type_indicator,
                                                 comparison_value='10_Momentum_1w.previous_value'),
            ),
            Condition(
                first_operand=Condition.Operand(operand_type=type_indicator,
                                                comparison_value='9_MovingAverage_1w.present_value'),
                operator='>',
                second_operand=Condition.Operand(operand_type=type_indicator,
                                                 comparison_value='4_MovingAverage_1w.present_value'),
            )
        ]

    def _assert_conditions(self, test_conditions, trading_system_conditions):

        self.assertEqual(len(trading_system_conditions), len(test_conditions))

        for n in range(len(test_conditions)):
            self.assertEqual(
                trading_system_conditions[n].first_operand.operand_type,
                test_conditions[n].first_operand.operand_type
            )
            self.assertEqual(
                trading_system_conditions[n].first_operand.comparison_value,
                test_conditions[n].first_operand.comparison_value
            )
            self.assertEqual(
                trading_system_conditions[n].operator,
                test_conditions[n].operator
            )
            self.assertEqual(
                trading_system_conditions[n].second_operand.operand_type,
                test_conditions[n].second_operand.operand_type
            )
            self.assertEqual(
                trading_system_conditions[n].second_operand.comparison_value,
                test_conditions[n].second_operand.comparison_value
            )

    def test_list(self):
        self._create_exchanges()

        with self.subTest(case='New and empty TradingSystemManager should return empty list'):
            ts_manager = TradingSystemManager(
                exchange_manager=app.exchange_manager,
                indicator_manager=app.indicator_manager
            )
            self.assertEqual(len(ts_manager.list()), 0)

        with self.subTest(case='Try to create trading system '
                               'TradingSystemManager should return list with the trading system'):
            ts_manager = TradingSystemManager(
                exchange_manager=app.exchange_manager,
                indicator_manager=app.indicator_manager
            )

            settings = TradingSystemSettingsLoader.correct_settings()
            trading_system = ts_manager.create(
                name=settings[0].get('name'),
                settings=settings[0].get('settings')
            )

            self.assertEqual(len(ts_manager.list()), 1)
            self.assertIn(trading_system, ts_manager.list())

        with self.subTest(case='Try to create 10 trading systems '
                               'TradingSystemManager should return list with 10 trading systems'):
            ts_manager = TradingSystemManager(
                exchange_manager=app.exchange_manager,
                indicator_manager=app.indicator_manager
            )

            created_trading_systems = []

            for n in range(10):
                created_trading_systems.append(ts_manager.create(
                    name=f'{settings[0].get("name")} {n}',
                    settings=settings[0].get('settings')
                ))

            self.assertEqual(len(ts_manager.list()), 10)
            self.assertEqual(ts_manager.list(), created_trading_systems)


class TestTradingSystemSettingsValidator(TestCase):

    def setUp(self) -> None:
        reset_managers()

        app.exchange_manager.create(name='ByBit', deal_opening_method='open_deal')
        app.exchange_manager.create(name='StormGain', deal_opening_method='send_message')

    def test_validate(self):
        correct_settings = TradingSystemSettingsLoader.correct_settings()

        with self.subTest(case='Test correct TradingSystemSettings'):
            self.assertIsNone(TradingSystemSettingsValidator.validate(
                name=correct_settings[0].get('name'),
                settings=correct_settings[0].get('settings'),
                exchange_manager=app.exchange_manager,
            ))

        with self.subTest(case='If "name" is empty validator should raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['name'] = ''

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager,
                )

        with self.subTest(case='If "settings" are empty validator should raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings'] = ''

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager,
                )

        with self.subTest(case='If "indicators" are empty validator should raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['indicators'] = ''

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager,
                )

        with self.subTest(case='If "indicators" have bad format raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['indicators'] = {'bad_attr': 123}

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager,
                )

        with self.subTest(case='If "indicators" contain indicator with bad interval'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['indicators'][0]['interval'] = '18m'

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager,
                )

        with self.subTest(case='If "exchanges" are empty validator should raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['exchanges'] = ''

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager,
                )

        with self.subTest(case='If "conditions_to_buy" are empty validator should raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['conditions_to_buy'] = ''

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager
                )

        with self.subTest(case='If "conditions_to_buy" have bad format raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['conditions_to_buy'] = {'bad_attr': 123}

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager
                )

        with self.subTest(case='If "conditions_to_sell" are empty validator should raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['conditions_to_sell'] = ''

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager
                )

        with self.subTest(case='If "conditions_to_buy" have bad format raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['conditions_to_sell'] = {'bad_attr': 123}

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager
                )

        with self.subTest(case='If "uptrend_conditions" are empty validator should raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['uptrend_conditions'] = ''

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager
                )

        with self.subTest(case='If "uptrend_conditions" have bad format raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['uptrend_conditions'] = {'bad_attr': 123}

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager
                )

        with self.subTest(case='If "downtrend_conditions" are empty validator should raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['downtrend_conditions'] = ''

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager
                )

        with self.subTest(case='If "downtrend_conditions" have bad format raise ValueError'):
            bad_settings = copy.deepcopy(correct_settings)
            bad_settings[0]['settings']['downtrend_conditions'] = {'bad_attr': 123}

            with self.assertRaises(ValueError):
                TradingSystemSettingsValidator.validate(
                    name=bad_settings[0].get('name'),
                    settings=bad_settings[0].get('settings'),
                    exchange_manager=app.exchange_manager
                )


class TestOperand(TestCase):
    def setUp(self) -> None:
        reset_managers()

    def test_get_operand_value(self):
        exchange = app.exchange_manager.create(name='Test', deal_opening_method='open_deal')
        btc = app.symbol_manager.create(
            base_currency='BTC',
            quote_currency='USDT',
            exchanges=exchange,
            deal_opening_params={'qty': 2}
        )

        mom = app.indicator_manager.create(
            name='1h_Momentum_10',
            indicator_type='Momentum',
            interval='1h',
            period=10,
        )

        ma = app.indicator_manager.create(
            name='1h_MovingAverage_4',
            indicator_type='MovingAverage',
            interval='1h',
            period=4,
        )

        indicator_values = [
            app.indicator_value_manager.create(indicator=mom, symbol=btc, present_value=7, previous_value=-8.76),
            app.indicator_value_manager.create(indicator=ma, symbol=btc, present_value=7, previous_value=-8.76),
        ]

        with self.subTest(case='When operand_type is INDICATOR_VALUE, method should return right indicator value'):
            operand = Condition.Operand(
                operand_type=Condition.Operand.OperandType.INDICATOR_VALUE,
                comparison_value='1h_Momentum_10.present_value'
            )

            self.assertEqual(operand.get_operand_value(indicator_values=indicator_values), 7)

        with self.subTest(case='When operand_type is NUMBER, '
                               'method should return the value that was specified when the operand was created'):
            operand = Condition.Operand(
                operand_type=Condition.Operand.OperandType.NUMBER,
                comparison_value='0.76'
            )

            self.assertEqual(operand.get_operand_value(indicator_values=indicator_values), 0.76)


class TestCondition(TestCase):
    def setUp(self) -> None:
        reset_managers()

        first_operand = Condition.Operand(
            operand_type=Condition.Operand.OperandType.NUMBER,
            comparison_value='8'
        )
        second_operand = Condition.Operand(
            operand_type=Condition.Operand.OperandType.NUMBER,
            comparison_value='-0.76'
        )
        self.condition = Condition(
            first_operand=first_operand,
            operator='>',
            second_operand=second_operand,
        )

    def test_is_satisfied(self):

        with self.subTest(case='Test method, when operator is ">"'):
            self.condition.operator = '>'

            self.assertTrue(self.condition.is_satisfied(first_operand_value=2, second_operand_value=-0.56))
            self.assertFalse(self.condition.is_satisfied(first_operand_value=2, second_operand_value=2))
            self.assertFalse(self.condition.is_satisfied(first_operand_value=2, second_operand_value=2.0003))

        with self.subTest(case='Test method, when operator is "<"'):
            self.condition.operator = '<'

            self.assertTrue(self.condition.is_satisfied(first_operand_value=-0.57, second_operand_value=-0.56))
            self.assertFalse(self.condition.is_satisfied(first_operand_value=2, second_operand_value=2))
            self.assertFalse(self.condition.is_satisfied(first_operand_value=2, second_operand_value=1.0003))

        with self.subTest(case='Test method, when operator is "="'):
            self.condition.operator = '='

            self.assertTrue(self.condition.is_satisfied(first_operand_value=-0.57, second_operand_value=-0.57))
            self.assertFalse(self.condition.is_satisfied(first_operand_value=2, second_operand_value=8))
            self.assertFalse(self.condition.is_satisfied(first_operand_value=2, second_operand_value=1.0003))
