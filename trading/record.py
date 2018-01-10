from datetime import datetime

import config as cfg
import constants as c

from data.store import FileStore
from data.feed import CSVDataFeed
from utils.dates import Timeframe

from portfolio.portfolio import Portfolio
from portfolio.asset import Asset
from portfolio.balance import Balance, BalanceType
from portfolio.performance import PerformanceTracker

from trading.order import Order
from trading.order import OrderType, OrderStatus

import utils.files

# https://www.backtrader.com/docu/position.html
# https://www.backtrader.com/docu/order.html
# https://www.backtrader.com/docu/trade.html#backtrader.trade.Trade
# https://www.backtrader.com/docu/datafeed.html
# https://www.backtrader.com/docu/writer.html
# https://www.backtrader.com/docu/plotting/plotting.html
# https://www.backtrader.com/docu/live/live.html
# https://www.backtrader.com/docu/broker.html
# https://www.backtrader.com/docu/strategy.html
# https://www.backtrader.com/docu/cerebro.html

CONFIG_FNAME = 'config'
ORDERS_FNAME = 'orders'
OHLCV_FNAME = 'ohlcv'
PORTFOLIO_FNAME = 'portfolio'
PERFORMANCE_FNAME = 'performance'
METRICS_FNAME = 'metrics'
BALANCE_FNAME = 'balance'

class Record():
    def __init__(self, config, portfolio, balance, store):
        self.config = config
        self.portfolio = portfolio
        self.balance = balance
        self.store = store
        self.orders = {}
        self.metrics = {}
        self.ohlcv = None
        self.other_data = None

    def save(self):
        self.store.save_json(CONFIG_FNAME, self.config)
        self.store.save_json(METRICS_FNAME, self.metrics)
        self.store.save_json(BALANCE_FNAME, self.balance.to_dict())
        self.save_portfolio()
        self.save_orders()
        self.save_ohlcv()

    def save_portfolio(self):
        dct = self.portfolio.to_dict()
        self.store.save_json(PORTFOLIO_FNAME, dct)

    def save_orders(self):
        dct = {}
        for id_,order in self.orders.items():
            dct[id_] = order.to_dict()
        self.store.save_json(ORDERS_FNAME, dct)

    def save_ohlcv(self):
        if self.ohlcv:
            self.store.df_to_csv(self.ohlcv, OHLCV_FNAME)

    @classmethod
    def load(self, root_dir):
        store = FileStore(root_dir)
        config = store.load_json(CONFIG_FNAME)

        balance = store.load_json(BALANCE_FNAME)
        balance = Balance.from_dict(balance)

        portfolio = store.load_json(PORTFOLIO_FNAME)
        portfolio = Portfolio.from_dict(portfolio)

        orders = store.load_json(ORDERS_FNAME)
        orders = {o['id']: Order.from_dict(o) for o in orders.values()}

        ohlcv = store.csv_to_df(OHLCV_FNAME, index='time_epoch')
        metrics = store.load_json(METRICS_FNAME)

        record = Record(
            config=config,
            portfolio=portfolio,
            balance=balance,
            store=store
        )
        record.orders = orders
        record.ohlcv = ohlcv
        record.metrics = metrics

        return record
