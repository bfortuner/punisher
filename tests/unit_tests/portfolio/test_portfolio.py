import math
import pytest
from copy import deepcopy

from punisher.trading.order_manager import (build_limit_buy_order,
                                            build_limit_sell_order,
                                            process_orders)
class TestSingleExchangePortfolio:

    def test_portfolio(self, portfolio, paperexchange):
        assert portfolio is not None
        assert portfolio.positions_value == 0.0
        assert portfolio.total_value == 0.0
        assert portfolio.starting_cash == 0.0
        assert portfolio.cash == 0.0
        # setting some default cash values for these tests
        portfolio.balance.update(portfolio.cash_currency, 20000, 0.0)
        paperexchange.balance = deepcopy(portfolio.balance)
        portfolio.starting_balance.update(portfolio.cash_currency, 20000, 0.0)
        portfolio.perf.starting_cash = 20000

        assert portfolio.positions_value == 0.0
        assert portfolio.total_value == 20000.0
        assert portfolio.cash == 20000

    def test_new_long_position_buy(self, portfolio, paperexchange, asset):
        quantity = 1.0
        price = 10000.0
        time = paperexchange.data_provider.get_time()
        print("START TIME = {}".format(time))
        buy_order = build_limit_buy_order(
            portfolio.balance, paperexchange, asset, quantity, price, time)
        updated_orders = process_orders(
            paperexchange, portfolio.balance, [buy_order])

        # Pre portfolio update:
        assert portfolio.cash == 20000
        assert portfolio.total_value == 20000

        latest_prices = { asset.symbol: 10000 }
        print("updated_order trade time {}".format(updated_orders[0].trades[0].trade_time))
        portfolio.update(time, updated_orders, latest_prices)
        portfolio.update_performance(
            time, time + paperexchange.data_provider.feed.timeframe.delta)

        assert portfolio.cash == 10000
        assert portfolio.positions_value == 10000
        # cash + positions_value = total value
        assert portfolio.total_value == 20000
        assert portfolio.positions[0].cost_price == 10000
        assert portfolio.positions[0].market_value == 10000
        assert portfolio.perf.pnl == 0.0

    def test_price_increase(self, portfolio, paperexchange, asset):
        latest_prices = { asset.symbol: 11000 }
        print(portfolio.positions)
        time = paperexchange.data_provider.get_time()
        portfolio.update(paperexchange.data_provider.get_time(), [], latest_prices)

        portfolio.update_performance(
            time, time + paperexchange.data_provider.feed.timeframe.delta)
        assert portfolio.cash == 10000
        assert portfolio.positions_value == 11000
        assert portfolio.total_value == 21000
        assert portfolio.positions[0].market_value == 11000
        assert portfolio.positions[0].cost_value == 10000
        # postion.market_value - position.cost_value = pnl
        assert portfolio.perf.pnl == 1000

    def test_existing_long_position_buy(self, portfolio, paperexchange, asset):
        quantity = 1.0
        price = 9000
        time = paperexchange.data_provider.get_time()
        buy_order = build_limit_buy_order(
            portfolio.balance, paperexchange, asset, quantity, price, time)

        updated_orders = process_orders(
            paperexchange, portfolio.balance, [buy_order])

        latest_prices = { asset.symbol: 9000 }
        portfolio.update(time, updated_orders, latest_prices)
        portfolio.update_performance(
            time, time + paperexchange.data_provider.feed.timeframe.delta)

        assert portfolio.cash == 1000
        assert portfolio.positions_value == 18000
        # cash + positions_value == total_value
        assert portfolio.total_value == 19000
        assert portfolio.positions[0].cost_price == 9500
        assert portfolio.positions[0].market_value == 18000
        assert portfolio.positions[0].cost_value == 19000
        # position.market_value - position.cost_value = pnl
        assert portfolio.perf.pnl == -1000 # price went down
