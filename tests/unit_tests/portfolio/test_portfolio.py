import math
import pytest
from datetime import datetime
from punisher.trading.order_manager import (build_limit_buy_order,
                                            build_limit_sell_order)
from punisher.trading.trade import TradeSide

class TestSingleExchangePortfolio:

    def test_portfolio(self, portfolio):
        assert portfolio is not None
        assert portfolio.positions_value == 0.0

        # setting some default cash values for these tests
        portfolio.cash = 20000
        portfolio.starting_cash = 20000
        portfolio.perf.starting_cash = 20000

    def test_new_long_position_buy(self, portfolio, trade, asset):
        quantity = 1.0
        price = 10000.0
        trade.side = TradeSide.BUY
        trade.quantity = quantity
        trade.price = price

        latest_prices = { asset.symbol: 10000 }
        portfolio.update(datetime.utcnow(), [trade],latest_prices)

        assert portfolio.cash == 10000
        assert portfolio.positions[0].cost_price == 10000
        assert portfolio.perf.pnl == 0.0


    def test_price_increase(self, portfolio, asset):
        latest_prices = { asset.symbol: 11000 }
        print(portfolio.positions)
        portfolio.update(datetime.utcnow(), [], latest_prices)

        assert portfolio.positions[0].market_value == 11000
        assert portfolio.perf.pnl == 1000

    def test_existing_long_position_buy(self, portfolio, trade, asset):
        quantity = 1.0
        price = 9000
        trade.side = TradeSide.BUY
        trade.quantity = quantity
        trade.price = price

        latest_prices = { asset.symbol: 9000 }
        portfolio.update(datetime.utcnow(), [trade],latest_prices)

        assert portfolio.cash == 1000
        assert portfolio.positions[0].cost_price == 9500
        assert portfolio.perf.pnl == -1000 # price went down
