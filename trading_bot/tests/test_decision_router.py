from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from trading_bot import app
from trading_bot.services.decision_maker import DecisionMaker, DealSide
from trading_bot.services.decision_router import DecisionRouter
from trading_bot.tests.helpers import reset_managers
from trading_bot.tests.test_trading_systems import TradingSystemSettingsLoader


class TestDecisionRouter(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        reset_managers()

    async def test_route(self):
        mock_notifier = AsyncMock()
        mock_deal_opener = AsyncMock()

        stormgain = app.exchange_manager.create('StormGain', 'send_message')
        bybit = app.exchange_manager.create('ByBit', 'open_deal')

        settings = TradingSystemSettingsLoader.correct_settings()
        tr_system = app.trading_system_manager.create(
            name=settings[0]['name'],
            settings=settings[0]['settings']
        )

        btc_sg = app.symbol_manager.create(
            base_currency='BTC',
            quote_currency='USDT',
            exchanges=[stormgain],
            deal_opening_params={'qty': 7.8}
        )

        eth_bb = app.symbol_manager.create(
            base_currency='ETH',
            quote_currency='USDT',
            exchanges=[bybit],
            deal_opening_params={'qty': 9.8}
        )

        ltc_sg_bb = app.symbol_manager.create(
            base_currency='LTC',
            quote_currency='USDT',
            exchanges=[stormgain, bybit],
            deal_opening_params={'qty': 2}
        )

        with self.subTest(case='When exchange deal opening method is SEND_MESSAGE, '
                               'the method should call notifier'):

            decision = DecisionMaker.Decision(
                symbol=btc_sg,
                side=DealSide.BUY,
                trading_system=tr_system
            )

            await DecisionRouter(notifier=mock_notifier, deal_opener=mock_deal_opener).rout(decision)

            mock_deal_opener.open_deal.assert_not_called()
            mock_notifier.notify.assert_called_with(msg=str(decision))

        with self.subTest(case='When exchange deal opening method is OPEN_DEAL, '
                               'the method should call deal opener'):
            mock_notifier.reset_mock()
            mock_deal_opener.reset_mock()

            decision = DecisionMaker.Decision(
                symbol=eth_bb,
                side=DealSide.SELL,
                trading_system=tr_system
            )

            await DecisionRouter(notifier=mock_notifier, deal_opener=mock_deal_opener).rout(decision)

            mock_deal_opener.open_deal.assert_called_with(decision)
            mock_notifier.notify.assert_not_called()

        with self.subTest(case='When symbol has exchange with both deal opening method (OPEN_DEAL and SEND_MESSAGE), '
                               'the method should call deal opener and notifier'):
            mock_notifier.reset_mock()
            mock_deal_opener.reset_mock()

            decision = DecisionMaker.Decision(
                symbol=ltc_sg_bb,
                side=DealSide.SELL,
                trading_system=tr_system
            )

            await DecisionRouter(notifier=mock_notifier, deal_opener=mock_deal_opener).rout(decision)

            mock_deal_opener.open_deal.assert_called_with(decision)
            mock_notifier.notify.assert_called_with(msg=str(decision))
