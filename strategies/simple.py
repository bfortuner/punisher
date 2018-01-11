import random

import constants as c
from portfolio.asset import Asset
from trading import order_manager

from .strategy import Strategy


class SimpleStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def log_all(self, orders, data, ctx, time_utc):
        self.logger = ctx.logger
        if self.logger is not None:
            self.log_epoch_time(time_utc)
            self.log_ohlcv(data)
            self.log_orders(orders)
            self.log_performance(ctx)
            self.log_balance(ctx)
            self.log_positions(ctx)
            self.log_metrics(ctx)

    def handle_data(self, data, ctx):
        orders = []
        asset = Asset(c.ETH, c.BTC)
        price = data['close']
        quantity = 1.0

        if random.random() > 0.5:
            order = order_manager.build_limit_buy_order(
                ctx.exchange, asset, price, quantity)
        else:
            order = order_manager.build_limit_sell_order(
                ctx.exchange, asset, price, quantity)

        orders.append(order)

        # Add Metrics and OHLCV to Record
        self.update_metric('SMA', 5.0, ctx)
        self.update_metric('RSI', 10.0, ctx)
        self.update_ohlcv(data, ctx)

        self.log_all(orders, data, ctx, data['time_utc'])

        return orders
