import os
import datetime
import random
import argparse
from copy import deepcopy

import punisher.config as cfg
import punisher.constants as c
from punisher.data.feed import CSVDataFeed
from punisher.data.feed import ExchangeDataFeed
from punisher.exchanges.exchange import load_exchange
from punisher.exchanges.exchange import load_feed_based_paper_exchange
from punisher.exchanges.exchange import load_ccxt_based_paper_exchange
from punisher.portfolio.asset import Asset
from punisher.portfolio.balance import Balance, BalanceType
from punisher.portfolio.portfolio import Portfolio
from punisher.portfolio.performance import PerformanceTracker
from punisher.trading import order_manager
from punisher.trading import runner
from punisher.trading.runner import TradeMode
from punisher.utils.dates import Timeframe

from .strategy import Strategy



parser = argparse.ArgumentParser(description='Punisher Dash Vizualizer')
parser.add_argument('-n', '--name', help='name of your experiment', default='default', type=str)
parser.add_argument('-p', '--plot', help='include Dash visualizations?', action="store_true")
parser.add_argument('-m', '--mode', help='TradeMode - backtest, simulate, live', default='backtest', type=str)
parser.add_argument('-v', '--verbose', help='log to console?', action="store_true")
parser.add_argument('-c', '--cash', help='starting cash', default=1.0, type=float)
parser.add_argument('-a', '--asset', help='ETH/BTC (quote/base)', default=None, type=str)
parser.add_argument('-q', '--quantity', help='# of base coin to purchase', default=.05, type=float)
parser.add_argument('-t', '--timeframe', help='timeframe of OHLCV trading data (1m, 5m, 30m, 1h)', default='30m', type=str)
parser.add_argument('-ohlcv', '--ohlcv_fpath', help='path to OHLCV csv file', default='', type=str)
parser.add_argument('-ex', '--exchange_id', help='CCXT exchange name', default='', type=str)

class SimpleStrategy(Strategy):
    def __init__(self, asset, quantity):
        super().__init__()
        self.asset = asset
        self.quantity = quantity

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
        price = data['close']

        if random.random() > 0.5:
            order = order_manager.build_limit_buy_order(
                ctx.exchange, self.asset, self.quantity, price)
        else:
            order = order_manager.build_market_sell_order(
                ctx.exchange, self.asset, self.quantity)
        orders.append(order)

        # Optionally cancel pending orders (LIVE trading)
        #pending_orders = ctx.exchange.fetch_open_orders(asset)
        cancel_ids = []

        # Add Metrics and OHLCV to Record
        self.update_metric('SMA', 5.0, ctx)
        self.update_metric('RSI', 10.0, ctx)
        self.update_ohlcv(data, ctx)

        self.log_all(orders, data, ctx, data['time_utc'])
        return {
            'orders': orders,
            'cancel_ids': cancel_ids
        }


if __name__ == "__main__":
    args = parser.parse_args()
    experiment_name = args.name + '_' + args.mode
    trade_mode = TradeMode[args.mode.upper()]
    timeframe = Timeframe.from_id(args.timeframe)
    starting_cash = args.cash
    asset = Asset.from_symbol(args.asset)
    quantity = args.quantity
    cash_currency = asset.quote
    plot = args.plot
    verbose = args.verbose
    ohlcv_fpath = args.ohlcv_fpath
    exchange_id = args.exchange_id

    print(("\nExperiment \n----------------------\n"
         + "Name: {:s}\n"
         + "TradeMode: {:s}\n"
         + "Timeframe: {:s}\n"
         + "Asset: {:s}\n"
         + "Quantity: {:.4f}\n"
         + "StartingCash: {:4f}\n"
         + "OHLCV: {:s}\n"
         + "Exchange: {:s}\n"
         + "----------------------\n").format(
         experiment_name, trade_mode.name, timeframe.id, asset.symbol,
         quantity, starting_cash, ohlcv_fpath, exchange_id))

    print(("To visualize, run: `python -m punisher.charts.dash_charts.dash_record --name {:s}`\n").format(experiment_name))

    strategy = SimpleStrategy(asset, quantity)
    balance = Balance(
        cash_currency=cash_currency,
        starting_cash=starting_cash
    )
    perf_tracker = PerformanceTracker(
        starting_cash=starting_cash,
        timeframe=timeframe
    )
    portfolio = Portfolio(
        starting_cash=starting_cash,
        perf_tracker=perf_tracker, # option to override, otherwise default
        positions=None # option to override with existing positions
    )

    if trade_mode is TradeMode.BACKTEST:
        feed = CSVDataFeed(
            fpath=ohlcv_fpath,
            start=None, # Usually None for backtest, but its possible to filter the csv
            end=None
        )
        exchange = load_feed_based_paper_exchange(balance, feed)
        runner.backtest(experiment_name, exchange, balance,
                        portfolio, feed, strategy)

    elif trade_mode is TradeMode.SIMULATE:
        exchange = load_ccxt_based_paper_exchange(balance, exchange_id)
        feed = ExchangeDataFeed(
            exchange=exchange,
            assets=[asset],
            timeframe=timeframe,
            start=datetime.datetime.utcnow(),
            end=None
        )
        runner.simulate(experiment_name, exchange, balance,
                        portfolio, feed, strategy)

    elif trade_mode is TradeMode.LIVE:
        exchange = load_exchange(exchange_id)
        feed = ExchangeDataFeed(
            exchange=exchange,
            assets=[asset],
            timeframe=timeframe,
            start=datetime.datetime.utcnow(),
            end=None
        )
        runner.live(experiment_name, exchange, balance,
                        portfolio, feed, strategy)
