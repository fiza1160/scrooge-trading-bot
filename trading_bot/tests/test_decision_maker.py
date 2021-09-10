from datetime import datetime, timedelta
from random import random
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from trading_bot import app
from trading_bot.models.trading_systems import Condition
from trading_bot.services.decision_maker import DecisionMaker, DealSide
from trading_bot.tests.helpers import reset_managers
from trading_bot.tests.test_trading_systems import TradingSystemSettingsLoader


class TestDecisionMaker(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        reset_managers()

    @patch('trading_bot.services.decision_maker.DecisionMaker._call_router')
    async def test__decide(self, mock__call_router):

        with self.subTest(case='When there are no symbols,'
                               'method should do nothing'):

            await DecisionMaker(
                trading_system_manager=app.trading_system_manager,
                symbol_manager=app.symbol_manager,
                indicator_value_manager=app.indicator_value_manager,
                decision_router=app.decision_router,
            ).decide()

            self.assertEqual(app.symbol_manager.list(), [])
            mock__call_router.assert_not_called()

        with self.subTest(case='When all symbols are paused,'
                               'method should do nothing'):
            mock__call_router.reset_mock()

            symbol = app.symbol_manager.create(
                base_currency='BTC',
                quote_currency='USDT',
                exchanges=[
                    app.exchange_manager.create('ByBit', 'open_deal'),
                    app.exchange_manager.create('StormGain', 'send_message')
                ],
                deal_opening_params={'qty': 5}
            )
            symbol.pause = True

            await DecisionMaker(
                trading_system_manager=app.trading_system_manager,
                symbol_manager=app.symbol_manager,
                indicator_value_manager=app.indicator_value_manager,
                decision_router=app.decision_router,
            ).decide()

            mock__call_router.assert_not_called()

        with self.subTest(case='When there are no trading systems,'
                               'method should do nothing'):

            mock__call_router.reset_mock()

            await DecisionMaker(
                trading_system_manager=app.trading_system_manager,
                symbol_manager=app.symbol_manager,
                indicator_value_manager=app.indicator_value_manager,
                decision_router=app.decision_router,
            ).decide()

            self.assertEqual(app.trading_system_manager.list(), [])
            mock__call_router.assert_not_called()

        with self.subTest(case='When there are no indicator values for all required indicators,'
                               'method should do nothing'):
            mock__call_router.reset_mock()

            settings = TradingSystemSettingsLoader.correct_settings()
            app.trading_system_manager.create(
                name=settings[0]['name'],
                settings=settings[0]['settings']
            )

            await DecisionMaker(
                trading_system_manager=app.trading_system_manager,
                symbol_manager=app.symbol_manager,
                indicator_value_manager=app.indicator_value_manager,
                decision_router=app.decision_router,
            ).decide()

            self.assertEqual(app.indicator_value_manager.list(), [])
            mock__call_router.assert_not_called()

        with self.subTest(case='When not all values of the required indicators are actual,'
                               'method should do nothing'):
            mock__call_router.reset_mock()

            symbol = app.symbol_manager.list()[0]
            symbol.pause = False

            tr_system = app.trading_system_manager.list()[0]
            indicator_values = []
            for indicator in tr_system.indicators:
                indicator_values.append(
                    app.indicator_value_manager.create(
                        indicator=indicator,
                        symbol=symbol,
                        present_value=-67,
                        previous_value=8.6598,
                    )
                )
            indicator_values[0].updated_at = datetime.now() - timedelta(hours=8)

            await DecisionMaker(
                trading_system_manager=app.trading_system_manager,
                symbol_manager=app.symbol_manager,
                indicator_value_manager=app.indicator_value_manager,
                decision_router=app.decision_router,
            ).decide()

            self.assertFalse(indicator_values[0].is_actual())
            mock__call_router.assert_not_called()

        with self.subTest(case='When indicator values do not satisfy buy or sell deal opening conditions,'
                               'method should do nothing'):
            mock__call_router.reset_mock()

            app.indicator_value_manager._indicator_values = []
            app.indicator_value_manager._indicator_values_by_key = {}

            tr_system = app.trading_system_manager.list()[0]
            indicator_values = []
            for indicator in tr_system.indicators:
                indicator_values.append(
                    app.indicator_value_manager.create(
                        indicator=indicator,
                        symbol=symbol,
                        present_value=0,
                        previous_value=0,
                    )
                )

            await DecisionMaker(
                trading_system_manager=app.trading_system_manager,
                symbol_manager=app.symbol_manager,
                indicator_value_manager=app.indicator_value_manager,
                decision_router=app.decision_router,
            ).decide()

            mock__call_router.assert_not_called()

        with self.subTest(case='When the values of the indicators satisfy the conditions of buy,'
                               'method should create Decision(side=Buy) and call decision_router'):
            mock__call_router.reset_mock()

            app.indicator_value_manager._indicator_values = []
            app.indicator_value_manager._indicator_values_by_key = {}

            symbol = app.symbol_manager.list()[0]
            symbol.pause = False

            app.indicator_value_manager.create(
                indicator=app.indicator_manager.get('10_Momentum_1h'),
                symbol=symbol,
                present_value=5,
                previous_value=2,
            )

            app.indicator_value_manager.create(
                indicator=app.indicator_manager.get('4_MovingAverage_1h'),
                symbol=symbol,
                present_value=18,
                previous_value=2,
            )

            app.indicator_value_manager.create(
                indicator=app.indicator_manager.get('9_MovingAverage_1h'),
                symbol=symbol,
                present_value=10,
                previous_value=2,
            )

            await DecisionMaker(
                trading_system_manager=app.trading_system_manager,
                symbol_manager=app.symbol_manager,
                indicator_value_manager=app.indicator_value_manager,
                decision_router=app.decision_router,
            ).decide()

            self.assertTrue(symbol.pause)
            mock__call_router.assert_called_with(
                side=DealSide.BUY,
                symbol=symbol,
                trading_system=app.trading_system_manager.list()[0],
            )

        with self.subTest(case='When the values of the indicators satisfy the conditions of sell,'
                               'method should create Decision(side=Sell) and call decision_router'):
            mock__call_router.reset_mock()

            app.indicator_value_manager._indicator_values_by_key = {}
            app.indicator_value_manager._indicator_values = []
            app.indicator_value_manager._indicator_values_by_key = {}

            symbol = app.symbol_manager.list()[0]
            symbol.pause = False

            app.indicator_value_manager.create(
                indicator=app.indicator_manager.get('10_Momentum_1h'),
                symbol=symbol,
                present_value=-5,
                previous_value=-2,
            )

            app.indicator_value_manager.create(
                indicator=app.indicator_manager.get('4_MovingAverage_1h'),
                symbol=symbol,
                present_value=-18,
                previous_value=2,
            )

            app.indicator_value_manager.create(
                indicator=app.indicator_manager.get('9_MovingAverage_1h'),
                symbol=symbol,
                present_value=-2,
                previous_value=2,
            )

            await DecisionMaker(
                trading_system_manager=app.trading_system_manager,
                symbol_manager=app.symbol_manager,
                indicator_value_manager=app.indicator_value_manager,
                decision_router=app.decision_router,
            ).decide()

            self.assertTrue(symbol.pause)
            mock__call_router.assert_called_with(
                side=DealSide.SELL,
                symbol=symbol,
                trading_system=app.trading_system_manager.list()[0],
            )

    def test__check_deal_opening_conditions(self):

        condition_ind_value = Condition(
            first_operand=Condition.Operand(
                operand_type=Condition.Operand.OperandType.INDICATOR_VALUE,
                comparison_value='10_Momentum_1h.present_value'
            ),
            operator='>',
            second_operand=Condition.Operand(
                operand_type=Condition.Operand.OperandType.INDICATOR_VALUE,
                comparison_value='10_Momentum_1h.previous_value'
            ),
        )

        condition_number = Condition(
            first_operand=Condition.Operand(
                operand_type=Condition.Operand.OperandType.INDICATOR_VALUE,
                comparison_value='4_MovingAverage_5m.present_value'
            ),
            operator='=',
            second_operand=Condition.Operand(
                operand_type=Condition.Operand.OperandType.NUMBER,
                comparison_value='8.5456'
            ),
        )

        conditions = [condition_number, condition_ind_value]

        btc = app.symbol_manager.create(
            base_currency='BTC',
            quote_currency='USDT',
            exchanges=[
                app.exchange_manager.create('ByBit', 'open_deal')
            ],
            deal_opening_params={'qty': 6.78}
        )

        mom = app.indicator_manager.create(
            name='10_Momentum_1h',
            indicator_type='Momentum',
            interval='1h',
            period=10,
        )

        ma = app.indicator_manager.create(
            name='4_MovingAverage_5m',
            indicator_type='MovingAverage',
            interval='5m',
            period=4,
        )

        with self.subTest(case='When the indicator values satisfy all condition, '
                               'method should return True.'):
            values = [
                app.indicator_value_manager.create(
                    indicator=mom,
                    symbol=btc,
                    present_value=7.87,
                    previous_value=-2,
                ),
                app.indicator_value_manager.create(
                    indicator=ma,
                    symbol=btc,
                    present_value=8.5456,
                    previous_value=-2,
                )
            ]

            self.assertTrue(app.decision_maker._check_deal_opening_conditions(
                indicator_values=values,
                conditions=conditions
            ))

        with self.subTest(case='When at least one of the indicator values do not satisfy the condition, '
                               'method should return False.'):
            app.indicator_value_manager.get(indicator=ma, symbol=btc).present_value = 8.545

            self.assertFalse(app.decision_maker._check_deal_opening_conditions(
                indicator_values=values,
                conditions=conditions
            ))

    def test__get_actual_indicator_values(self):

        btc = app.symbol_manager.create(
            base_currency='BTC',
            quote_currency='USDT',
            exchanges=[
                app.exchange_manager.create('ByBit', 'open_deal'),
                app.exchange_manager.create('StormGain', 'send_message'),
            ],
            deal_opening_params={'qty': 5}
        )

        settings = TradingSystemSettingsLoader.correct_settings()
        tr_system = app.trading_system_manager.create(
            name=settings[0]['name'],
            settings=settings[0]['settings']
        )

        with self.subTest(case='When there are no indicator values, '
                               'should return empty list'):
            self.assertEqual(app.decision_maker._get_actual_indicator_values(symbol=btc, trading_system=tr_system), [])

        with self.subTest(case='Method should return only actual indicators values'):
            actual_value = app.indicator_value_manager.create(
                indicator=app.indicator_manager.get('10_Momentum_1h'),
                symbol=btc,
                previous_value=67,
                present_value=-8.98,
            )

            not_actual_value = app.indicator_value_manager.create(
                indicator=app.indicator_manager.get('4_MovingAverage_1h'),
                symbol=btc,
                previous_value=67,
                present_value=-8.98,
            )
            not_actual_value.updated_at -= timedelta(hours=4)

            values = app.decision_maker._get_actual_indicator_values(symbol=btc, trading_system=tr_system)

            self.assertEqual(len(values), 1)
            self.assertIn(actual_value, values)
            self.assertNotIn(not_actual_value, values)

    def test__all_required_indicators_has_actual_values(self):
        btc = app.symbol_manager.create(
            base_currency='BTC',
            quote_currency='USDT',
            exchanges=[
                app.exchange_manager.create('ByBit', 'open_deal'),
                app.exchange_manager.create('StormGain', 'send_message'),
            ],
            deal_opening_params={'qty': 5}
        )

        settings = TradingSystemSettingsLoader.correct_settings()
        tr_system = app.trading_system_manager.create(
            name=settings[0]['name'],
            settings=settings[0]['settings']
        )

        for n in range(len(tr_system.indicators) - 1):
            app.indicator_value_manager.create(
                indicator=tr_system.indicators[n],
                symbol=btc,
                present_value=random,
                previous_value=random,
            )

        with self.subTest(case='When there is no value for at least one trading system`s indicator,'
                               'method should return False'):
            ind_values = app.indicator_value_manager.list()
            self.assertEqual(len(ind_values), len(tr_system.indicators) - 1)
            self.assertFalse(app.decision_maker._all_required_indicators_has_values(tr_system, ind_values))

        with self.subTest(case='When all trading system`s indicators has actual values,'
                               'method should return True'):
            app.indicator_value_manager.create(
                indicator=tr_system.indicators[len(tr_system.indicators) - 1],
                symbol=btc,
                present_value=random,
                previous_value=random,
            )

            ind_values = app.indicator_value_manager.list()

            self.assertEqual(len(ind_values), len(tr_system.indicators))
            self.assertTrue(app.decision_maker._all_required_indicators_has_values(tr_system, ind_values))
