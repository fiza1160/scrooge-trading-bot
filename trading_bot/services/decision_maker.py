from enum import Enum, auto
import logging

from trading_bot.models.indicator_values import IndicatorValueManager, IndicatorValue
from trading_bot.models.symbols import Symbol, SymbolManager
from trading_bot.models.trading_systems import TradingSystem, TradingSystemManager, Condition
from trading_bot.services.decision_router import DecisionRouter

logger = logging.getLogger('logger')


class DealSide(Enum):
    BUY = auto()
    SELL = auto()


class DecisionMaker:
    class Decision:
        def __init__(
                self,
                symbol: Symbol,
                side: DealSide,
                trading_system: TradingSystem,
        ) -> None:
            self.symbol = symbol
            self.side = side
            self.trading_system = trading_system

        def __str__(self):
            return f'{self.symbol} {self.side} {self.trading_system}'

        def __repr__(self):
            return f'{self.symbol} {self.side} {self.trading_system}'

    def __init__(
            self,
            trading_system_manager: TradingSystemManager,
            symbol_manager: SymbolManager,
            indicator_value_manager: IndicatorValueManager,
            decision_router: DecisionRouter,
    ) -> None:
        self._trading_system_manager = trading_system_manager
        self._symbol_manager = symbol_manager
        self._indicator_value_manager = indicator_value_manager
        self._decision_router = decision_router

    async def decide(self) -> None:
        for symbol in self._symbol_manager.list():
            if not symbol.pause:
                for trading_system in self._trading_system_manager.list():
                    indicator_values = self._get_actual_indicator_values(symbol, trading_system)

                    if self._all_required_indicators_has_values(trading_system, indicator_values):
                        buy = await self._check_buy_conditions(indicator_values, trading_system)
                        sell = await self._check_sell_conditions(indicator_values, trading_system)

                        if buy or sell:
                            symbol.pause = True
                            side = DealSide.BUY if buy else DealSide.SELL
                            await self._call_router(
                                side=side,
                                symbol=symbol,
                                trading_system=trading_system,
                            )

    async def _call_router(self, side, symbol, trading_system):
        decision = self.Decision(
                symbol=symbol,
                side=side,
                trading_system=trading_system,
            )
        logger.info(f'{decision}')

        await self._decision_router.rout(decision=decision)

    def _get_actual_indicator_values(
            self,
            symbol: Symbol,
            trading_system: TradingSystem
    ) -> [IndicatorValue]:
        indicator_values = []
        for indicator in trading_system.indicators:
            indicator_value = self._indicator_value_manager.get(indicator=indicator, symbol=symbol)
            if indicator_value and indicator_value.is_actual():
                indicator_values.append(indicator_value)
        return indicator_values

    @staticmethod
    def _all_required_indicators_has_values(
            trading_system: TradingSystem,
            indicator_values: [IndicatorValue]
    ) -> bool:
        return len(trading_system.indicators) == len(indicator_values)

    async def _check_sell_conditions(self, indicator_values, trading_system):
        return (self._check_conditions(indicator_values, trading_system.conditions_to_sell)
                and self._check_conditions(indicator_values, trading_system.downtrend_conditions))

    async def _check_buy_conditions(self, indicator_values, trading_system):
        return (self._check_conditions(indicator_values, trading_system.conditions_to_buy)
                and self._check_conditions(indicator_values, trading_system.uptrend_conditions))

    @staticmethod
    def _check_conditions(indicator_values: [IndicatorValue], conditions: [Condition]) -> bool:
        is_satisfied = True
        for condition in conditions:
            if is_satisfied:
                first_operand_value = condition.first_operand.get_operand_value(indicator_values=indicator_values)
                second_operand_value = condition.second_operand.get_operand_value(indicator_values=indicator_values)

                is_satisfied = condition.is_satisfied(
                    first_operand_value=first_operand_value,
                    second_operand_value=second_operand_value,
                )
        return is_satisfied
