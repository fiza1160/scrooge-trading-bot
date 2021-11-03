from enum import Enum, auto

from trading_bot.models.exchanges import Exchange, ExchangeManager
from trading_bot.models.indicator_values import IndicatorValue
from trading_bot.models.indicators import Indicator, IndicatorManager


class TradingSystemSettingsValidator:

    @staticmethod
    def validate(name: str, settings: {}, exchange_manager: ExchangeManager) -> None:
        if not name or not settings:
            raise ValueError

        indicators = settings.get('indicators')
        if not indicators:
            raise ValueError

        for indicator in indicators:
            if ('name' not in indicator or
                    'indicator_type' not in indicator or
                    'interval' not in indicator):
                raise ValueError

            if indicator['interval'] not in Indicator.Interval.valid_values:
                raise ValueError

        exchanges = settings.get('exchanges')
        if not exchanges:
            raise ValueError

        # At this step, all exchanges should already be created
        for exchange in exchanges:
            if not exchange_manager.get(exchange):
                raise ValueError

        for exchange in exchanges:
            if not exchange:
                raise ValueError

        TradingSystemSettingsValidator.validate_conditions(settings, 'conditions_to_buy')
        TradingSystemSettingsValidator.validate_conditions(settings, 'conditions_to_sell')
        TradingSystemSettingsValidator.validate_conditions(settings, 'uptrend_conditions')
        TradingSystemSettingsValidator.validate_conditions(settings, 'downtrend_conditions')

    @staticmethod
    def validate_conditions(settings: {}, conditions_name: str) -> None:
        conditions = settings.get(conditions_name)
        if not conditions:
            raise ValueError

        for condition in conditions:
            if ('first_operand' not in condition or
                    'operator' not in condition or
                    'second_operand' not in condition):
                raise ValueError

            if (condition['first_operand']['operand_type'] is None
                    or condition['first_operand']['value'] is None
                    or condition['second_operand']['operand_type'] is None
                    or condition['second_operand']['value'] is None):
                raise ValueError


class Condition:
    class Operand:
        class OperandType(Enum):
            INDICATOR_VALUE = auto()
            NUMBER = auto()

        def __init__(self, operand_type: OperandType, comparison_value: str) -> None:
            self.operand_type = operand_type
            self.comparison_value = comparison_value
            if operand_type is self.OperandType.NUMBER:
                self.comparison_value = float(self.comparison_value)

        def __str__(self) -> str:
            return str(self.comparison_value)

        def __repr__(self) -> str:
            return f'{self.comparison_value} {self.operand_type}'

        def get_operand_value(self, indicator_values: [IndicatorValue]) -> float:
            if self.operand_type is self.OperandType.NUMBER:
                return self.comparison_value
            else:
                indicator_name, value_name = self.comparison_value.split('.')
                for indicator_value in indicator_values:
                    if indicator_value.indicator.name == indicator_name:
                        return getattr(indicator_value, value_name)

    def __init__(self, first_operand: Operand, operator: str, second_operand: Operand) -> None:
        self.first_operand = first_operand
        self.operator = operator
        self.second_operand = second_operand
        self._operator_methods = {
            '>': self._more_than,
            '<': self._less_than,
            '=': self._equal,
        }

    def __str__(self) -> str:
        return f'{self.first_operand} {self.operator} {self.second_operand}'

    def __repr__(self) -> str:
        return f'{self.first_operand} {self.operator} {self.second_operand}'

    def is_satisfied(self, first_operand_value: float, second_operand_value: float) -> bool:
        return self._operator_methods[self.operator](first_operand_value, second_operand_value)

    @staticmethod
    def _less_than(first_operand_value: float, second_operand_value: float) -> bool:
        return first_operand_value < second_operand_value

    @staticmethod
    def _more_than(first_operand_value: float, second_operand_value: float) -> bool:
        return first_operand_value > second_operand_value

    @staticmethod
    def _equal(first_operand_value: float, second_operand_value: float) -> bool:
        return abs(first_operand_value - second_operand_value) < 1e-6


class TradingSystem:

    def __init__(
            self,
            name: str,
            indicators: [Indicator],
            exchanges: [Exchange],
            conditions_to_buy: [Condition],
            conditions_to_sell: [Condition],
            uptrend_conditions: [Condition],
            downtrend_conditions: [Condition],
    ) -> None:
        self.name = name
        self.indicators = indicators
        self.exchanges = exchanges
        self.conditions_to_buy = conditions_to_buy
        self.conditions_to_sell = conditions_to_sell
        self.uptrend_conditions = uptrend_conditions
        self.downtrend_conditions = downtrend_conditions

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'


class TradingSystemManager:
    validator = TradingSystemSettingsValidator

    def __init__(
            self,
            indicator_manager: IndicatorManager,
            exchange_manager: ExchangeManager,
    ) -> None:
        self._trading_systems = []
        self._indicator_manager = indicator_manager
        self._exchange_manager = exchange_manager

    def create(self, name: str, settings: {}) -> TradingSystem:
        self.validator.validate(name, settings, self._exchange_manager)

        indicators = self._indicators(settings['indicators'])
        exchanges = self._exchanges(settings['exchanges'])
        uptrend_conditions = self._create_conditions(settings['uptrend_conditions'])
        downtrend_conditions = self._create_conditions(settings['downtrend_conditions'])
        conditions_to_buy = self._create_conditions(settings['conditions_to_buy'])
        conditions_to_sell = self._create_conditions(settings['conditions_to_sell'])

        trading_system = TradingSystem(
            name=name,
            indicators=indicators,
            exchanges=exchanges,
            conditions_to_buy=conditions_to_buy,
            conditions_to_sell=conditions_to_sell,
            uptrend_conditions=uptrend_conditions,
            downtrend_conditions=downtrend_conditions,
        )

        self._trading_systems.append(trading_system)

        return trading_system

    def _indicators(self, indicators_settings: []) -> [Indicator]:
        indicators = []

        for setting in indicators_settings:
            indicator = self._indicator_manager.get(setting['name'])
            if not indicator:
                indicator = self._indicator_manager.create(
                    name=setting['name'],
                    indicator_type=setting['indicator_type'],
                    interval=setting['interval'],
                    optional=setting.get('optional')
                )

            indicators.append(indicator)

        return indicators

    def _exchanges(self, exchanges_settings: []) -> [Exchange]:
        exchanges = []

        for exchange_name in exchanges_settings:
            exchanges.append(self._exchange_manager.get(exchange_name))

        return exchanges

    @staticmethod
    def _create_conditions(conditions_settings: []) -> [Condition]:
        conditions = []
        for setting in conditions_settings:
            first_operand = Condition.Operand(
                operand_type=Condition.Operand.OperandType[setting['first_operand']['operand_type']],
                comparison_value=setting['first_operand']['value'],
            )
            second_operand = Condition.Operand(
                operand_type=Condition.Operand.OperandType[setting['second_operand']['operand_type']],
                comparison_value=setting['second_operand']['value'],
            )
            conditions.append(
                Condition(
                    first_operand=first_operand,
                    operator=setting['operator'],
                    second_operand=second_operand
                )
            )

        return conditions

    def list(self) -> [TradingSystem]:
        return self._trading_systems.copy()
