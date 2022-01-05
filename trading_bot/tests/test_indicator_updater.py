from datetime import datetime, timedelta
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, call, MagicMock, AsyncMock

from trading_bot import app
from trading_bot.models.indicators import IndicatorManager
from trading_bot.tests.helpers import reset_managers
from trading_bot.services.indicator_updater import IndicatorUpdater


class TestIndicatorUpdater(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        reset_managers()

    @patch('trading_bot.services.indicator_updater.IndicatorUpdater._update_indicator_values')
    @patch('trading_bot.services.indicator_updater.datetime')
    async def test__update(self, mock_datetime, mock_update_indicator_values):
        mom = app.indicator_manager.create(
            name='Momentum_1d',
            indicator_type='Momentum',
            interval='1d',
        )

        ma4 = app.indicator_manager.create(
            name='MovingAverage_1h_period4',
            indicator_type='MovingAverage',
            interval='1h',
            optional={'optInTimePeriod': 4}
        )

        ma9 = app.indicator_manager.create(
            name='MovingAverage_5m_period9',
            indicator_type='MovingAverage',
            interval='5m',
            optional={'optInTimePeriod': 9},
        )

        with self.subTest(case='Test updater for indicators '
                               '[Momentum_1d, MovingAverage_1h_period4, MovingAverage_5m_period9] '
                               'when when self._last_updates is empty (IndicatorsValues initialization)'
                               'IndicatorUpdater should call _update_indicator_values '
                               'for [Momentum_1d, MovingAverage_1h_period4, MovingAverage_5m_period9]'
                               'IndicatorUpdater should fill self._last_updates '
                               'IndicatorUpdater should update app.indicator_update_timeout (150)'):
            ind_updater = IndicatorUpdater(
                indicator_adapter=MagicMock(),
                decision_maker=MagicMock()
            )
            await ind_updater._update()

            calls = [call(mom), call(ma4), call(ma9)]
            mock_update_indicator_values.assert_has_calls(calls)

            self.assertIsNotNone(ind_updater._last_updates.get(mom))
            self.assertIsNotNone(ind_updater._last_updates.get(ma4))
            self.assertIsNotNone(ind_updater._last_updates.get(ma9))

            self.assertEqual(app.indicator_update_timeout, 150)
            self.assertTrue(ind_updater._values_updated)

        with self.subTest(case='Test updater for indicators '
                               '[Momentum_1d, MovingAverage_1h_period4, MovingAverage_5m_period9], '
                               'when self._last_updates is filled '
                               'and it is time to update all indicators. '
                               'IndicatorUpdater should call _update_indicator_values '
                               'for [Momentum_1d, MovingAverage_1h_period4, MovingAverage_5m_period9]'
                               'IndicatorUpdater should update self._last_updates '
                               'IndicatorUpdater should update app.indicator_update_timeout (150)'):
            mock_update_indicator_values.reset_mock()

            time_now = datetime.now()
            mock_datetime.now.return_value = time_now

            ind_updater = IndicatorUpdater(
                indicator_adapter=MagicMock(),
                decision_maker=MagicMock()
            )

            ind_updater._last_updates = {
                mom: time_now - timedelta(days=2),
                ma4: time_now - timedelta(hours=2),
                ma9: time_now - timedelta(minutes=6),
            }

            await ind_updater._update()

            calls = [call(mom), call(ma4), call(ma9)]
            mock_update_indicator_values.assert_has_calls(calls)

            self.assertEqual(len(ind_updater._last_updates), 3)
            self.assertEqual(ind_updater._last_updates[mom], time_now)
            self.assertEqual(ind_updater._last_updates[ma4], time_now)
            self.assertEqual(ind_updater._last_updates[ma9], time_now)

            self.assertEqual(app.indicator_update_timeout, 150)
            self.assertTrue(ind_updater._values_updated)

        with self.subTest(case='Test updater for indicators '
                               '[Momentum_1d, MovingAverage_1h_period4, MovingAverage_5m_period9], '
                               'when self._last_updates is filled '
                               'and it is time to update only [MovingAverage_1h_period4, MovingAverage_5m_period9]'
                               'IndicatorUpdater should call _update_indicator_values '
                               'only for [1MovingAverage_1h_period4, MovingAverage_5m_period9]'):
            mock_update_indicator_values.reset_mock()

            time_now = datetime.now()
            mock_datetime.now.return_value = time_now

            ind_updater = IndicatorUpdater(
                indicator_adapter=MagicMock(),
                decision_maker=MagicMock()
            )

            mom_last_updated_time = time_now - timedelta(hours=1)
            ind_updater._last_updates = {
                mom: mom_last_updated_time,
                ma4: time_now - timedelta(hours=2),
                ma9: time_now - timedelta(minutes=6),
            }

            await ind_updater._update()

            calls = [call(ma4), call(ma9)]
            mock_update_indicator_values.assert_has_calls(calls)

            self.assertEqual(len(ind_updater._last_updates), 3)
            self.assertEqual(ind_updater._last_updates[mom], mom_last_updated_time)
            self.assertEqual(ind_updater._last_updates[ma4], time_now)
            self.assertEqual(ind_updater._last_updates[ma9], time_now)

            self.assertEqual(app.indicator_update_timeout, 150)
            self.assertTrue(ind_updater._values_updated)

        with self.subTest(case='Test updater for indicators '
                               '[Momentum_1d, MovingAverage_1h_period4, MovingAverage_5m_period9], '
                               'and it is not time to update the indicators yet. '
                               'IndicatorUpdater should not call _update_indicator_values '
                               'IndicatorUpdater should not update self._last_updates '
                               'IndicatorUpdater should update app.indicator_update_timeout (150)'):
            mock_update_indicator_values.reset_mock()

            time_now = datetime.now()
            mock_datetime.now.return_value = time_now

            ind_updater = IndicatorUpdater(
                indicator_adapter=MagicMock(),
                decision_maker=MagicMock()
            )

            last_updated_time = time_now - timedelta(minutes=1)
            ind_updater._last_updates = {
                mom: last_updated_time,
                ma4: last_updated_time,
                ma9: last_updated_time,
            }

            await ind_updater._update()

            mock_update_indicator_values.assert_not_called()

            self.assertEqual(len(ind_updater._last_updates), 3)
            self.assertEqual(ind_updater._last_updates[mom], last_updated_time)
            self.assertEqual(ind_updater._last_updates[ma4], last_updated_time)
            self.assertEqual(ind_updater._last_updates[ma9], last_updated_time)

            self.assertEqual(app.indicator_update_timeout, 150)
            self.assertFalse(ind_updater._values_updated)

        with self.subTest(case='Test updater for indicators [], '
                               'IndicatorUpdater should raise exception'):
            reset_managers()
            with self.assertRaises(ValueError):
                await ind_updater._update()

    def test__its_time_to_update(self):
        ind_manager = IndicatorManager()
        indicator = ind_manager.create(
            name='Momentum_5m',
            indicator_type='Momentum',
            interval='5m',
        )

        with self.subTest(case='When self._last_updates is empty '
                               '_its_time_to_update should return True'):
            self.assertTrue(IndicatorUpdater(
                indicator_adapter=MagicMock(),
                decision_maker=MagicMock()
            )._its_time_to_update(indicator))

        with self.subTest(case='When self._last_updates does not contain last indicator updates time '
                               '_its_time_to_update should return True'):
            indicator_2 = ind_manager.create(
                name='MovingAverage_5m_period4',
                indicator_type='MovingAverage',
                interval='5m',
                optional={'optInTimePeriod': 4},
            )

            ind_updater = IndicatorUpdater(
                indicator_adapter=MagicMock(),
                decision_maker=MagicMock()
            )
            ind_updater._last_updates[indicator_2] = datetime.now()

            self.assertTrue(ind_updater._its_time_to_update(indicator))

        with self.subTest(case='When self._last_updates contains last indicator updates time '
                               'and last_update_time + indicator.interval.timeout = datetime.now()'
                               '_its_time_to_update should return True'):
            with patch('trading_bot.services.indicator_updater.datetime') as mock_datetime:
                datetime_now = datetime.now()
                mock_datetime.now.return_value = datetime_now

                ind_updater = IndicatorUpdater(
                    indicator_adapter=MagicMock(),
                    decision_maker=MagicMock()
                )
                ind_updater._last_updates[indicator] = datetime_now - timedelta(seconds=indicator.interval.timeout)

                self.assertTrue(ind_updater._its_time_to_update(indicator))

        with self.subTest(case='When self._last_updates contains last indicator updates time '
                               'and last_update_time + indicator.interval.timeout > datetime.now()'
                               '_its_time_to_update should return True'):
            ind_updater = IndicatorUpdater(
                indicator_adapter=MagicMock(),
                decision_maker=MagicMock()
            )
            ind_updater._last_updates[indicator] = (datetime.now() -
                                                    timedelta(seconds=indicator.interval.timeout) -
                                                    timedelta(seconds=60))

            self.assertTrue(ind_updater._its_time_to_update(indicator))

        with self.subTest(case='When self._last_updates contains last indicator updates time '
                               'and last_update_time + indicator.interval.timeout < datetime.now()'
                               '_its_time_to_update should return False'):
            ind_updater = IndicatorUpdater(
                indicator_adapter=MagicMock(),
                decision_maker=MagicMock()
            )
            ind_updater._last_updates[indicator] = datetime.now() - timedelta(seconds=20)

            self.assertFalse(ind_updater._its_time_to_update(indicator))

    @patch('trading_bot.services.indicator_updater.app.indicator_value_manager')
    async def test__update_indicator_values(self, mock_indicator_value_manager):
        ind_manager = IndicatorManager()
        indicator = ind_manager.create(
            name='Momentum_5m',
            indicator_type='Momentum',
            interval='5m',
        )

        mock_taapi_adapter = AsyncMock()
        mock_taapi_adapter.get_indicator_values.return_value = {
            'present_value': 768.7,
            'previous_value': -78,
        }

        with self.subTest(case='When symbols_manager.list() is empty, '
                               'method should raise exception'):
            self.assertEqual(len(app.symbol_manager.list()), 0)

            with self.assertRaises(ValueError):
                await IndicatorUpdater(
                    indicator_adapter=mock_taapi_adapter,
                    decision_maker=MagicMock()
                )._update_indicator_values(indicator)

        with self.subTest(case='When symbol.pause is True,  '
                               'method should do nothing'):
            by_bit = app.exchange_manager.create(
                name='ByBit',
                deal_opening_method='open_deal'
            )
            btc = app.symbol_manager.create(
                base_currency='BTC',
                quote_currency='USDT',
                exchanges=[by_bit],
                deal_opening_params={'qty': 2}
            )
            btc.pause = True

            await IndicatorUpdater(
                indicator_adapter=mock_taapi_adapter,
                decision_maker=MagicMock()
            )._update_indicator_values(indicator)

            mock_indicator_value_manager.update.assert_not_called()

        with self.subTest(case='When symbol.pause is False,  '
                               'method should update IndicatorValues for the indicator'):
            mock_taapi_adapter.get_indicator_values.return_value = {
                'present_value': 18,
                'previous_value': -6.76
            }

            by_bit = app.exchange_manager.create(
                name='ByBit',
                deal_opening_method='open_deal'
            )
            btc = app.symbol_manager.create(
                base_currency='BTC',
                quote_currency='USDT',
                exchanges=[by_bit],
                deal_opening_params={'qty': 2}
            )

            await IndicatorUpdater(
                indicator_adapter=mock_taapi_adapter,
                decision_maker=MagicMock()
            )._update_indicator_values(indicator)

            mock_indicator_value_manager.update.assert_called_with(
                symbol=btc,
                indicator=indicator,
                present_value=18,
                previous_value=-6.76,
            )

            with self.subTest(case='indicators_adapter.get_indicator_values raises Warning '
                                   'method should handle the exception and call the logger.'):
                # TODO add test
                pass
