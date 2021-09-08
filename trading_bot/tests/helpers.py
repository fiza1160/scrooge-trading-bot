from trading_bot import app, create_app


def init_app():
    create_app()


def reset_managers():
    create_app()

    app.symbol_manager._symbols = []
    app.exchange_manager._exchanges = []
    app.exchange_manager._exchanges_by_name = {}
    app.indicator_manager._indicators = []
    app.indicator_manager._indicators_by_name = {}
    app.indicator_value_manager._indicator_values = []
    app.indicator_value_manager._indicator_values_by_key = {}
    app.trading_system_manager._trading_systems = []
