import math
import pytest
from datetime import datetime
from copy import deepcopy

from punisher.trading.order_manager import (build_limit_buy_order,
                                            build_limit_sell_order,
                                            process_orders)
class TestSingleExchangePortfolio:

    def test_portfolio(self, portfolio, paperexchange):
        assert portfolio is not None
        assert portfolio.positions_value == 0.0

        # setting some default cash values for these tests
        portfolio.balance.update(portfolio.cash_currency, 20000, 0.0)
        paperexchange.balance = deepcopy(portfolio.balance)
        portfolio.starting_balance.update(portfolio.cash_currency, 20000, 0.0)
        portfolio.perf.starting_cash = 20000

    def test_new_long_position_buy(self, portfolio, paperexchange, asset):
        quantity = 1.0
        price = 10000.0
        start_time = datetime.utcnow()
        buy_order = build_limit_buy_order(
                    paperexchange, asset, quantity, price, start_time)
        updated_orders = process_orders(
                        paperexchange, portfolio.balance, [buy_order])

        # print("updated orders", updated_orders)
        # print("exchange balance: ", paperexchange.balance)
        # print("local balance: ", portfolio.balance)

        latest_prices = { asset.symbol: 10000 }
        portfolio.update(start_time, updated_orders, latest_prices)

        assert portfolio.cash == 10000
        assert portfolio.positions[0].cost_price == 10000
        assert portfolio.perf.pnl == 0.0


    def test_price_increase(self, portfolio, paperexchange, asset):
        latest_prices = { asset.symbol: 11000 }
        print(portfolio.positions)
        portfolio.update(datetime.utcnow(), [], latest_prices)

        assert portfolio.positions[0].market_value == 11000
        assert portfolio.perf.pnl == 1000

    def test_existing_long_position_buy(self, portfolio, paperexchange, asset):
        quantity = 1.0
        price = 9000
        start_time = datetime.utcnow()
        buy_order = build_limit_buy_order(
                    paperexchange, asset, quantity, price, start_time)

        updated_orders = process_orders(
                        paperexchange, portfolio.balance, [buy_order])

        latest_prices = { asset.symbol: 9000 }
        portfolio.update(start_time, updated_orders, latest_prices)

        assert portfolio.cash == 1000
        assert portfolio.positions[0].cost_price == 9500
        assert portfolio.perf.pnl == -1000 # price went down
