import os
import time
from enum import Enum, unique

import config as cfg
import constants as c

from data.store import DATA_STORES, FILE_STORE
from data.feed import EXCHANGE_FEED, CSV_FEED
from data.feed import load_feed
from utils.dates import Timeframe

from portfolio.portfolio import Portfolio
from portfolio.asset import Asset
from portfolio.balance import Balance, BalanceType
from portfolio.performance import PerformanceTracker

from trading import order_manager
from trading.record import Record
from exchanges.exchange import load_exchange

from utils.dates import str_to_date


DEFAULT_CONFIG = {
    'root': os.path.join(cfg.DATA_DIR, 'default'),
    'strategy': 'my_strategy',
    'exchange_id': c.PAPER,
    'cash_asset': c.BTC,
    'starting_cash': 1.0,
    'store': FILE_STORE,
    'feed': {
        'name': EXCHANGE_FEED,
        'fpath': os.path.join(cfg.DATA_DIR, 'default_feed.csv'),
        'symbols': ['ETH/BTC'],
        'timeframe': Timeframe.ONE_MIN.name,
        'start': '2018-01-01T00:00:00',
        'end': None,
    },
    'balance': {
        c.BTC: {'free': 1.0, 'used':0.0, 'total': 1.0},
        'free': {c.BTC: 1.0},
        'used': {c.BTC: 0.0},
        'total': {c.BTC: 1.0},
    }
}

class Context():
    def __init__(self, exchange, feed, record, config):
        self.exchange = exchange
        self.feed = feed
        self.record = record
        self.config = config

    @classmethod
    def from_config(self, cfg=DEFAULT_CONFIG):
        exchange = load_exchange(cfg['exchange_id'])
        store = DATA_STORES[cfg['store']](
            root=cfg['root'])
        feed = load_feed(
            name=cfg['feed']['name'],
            fpath=cfg['feed']['fpath'],
            exchange=exchange,
            assets=[Asset.from_symbol(a) for a in cfg['feed']['symbols']],
            timeframe=Timeframe[cfg['feed']['timeframe']],
            start=str_to_date(cfg['feed']['start']),
            end=str_to_date(cfg['feed']['end']),
        )
        perf = PerformanceTracker(
            starting_cash=cfg['starting_cash'],
            timeframe=Timeframe[cfg['feed']['timeframe']],
            store=store
        )
        record = Record(
            config=cfg,
            portfolio=Portfolio(cfg['starting_cash'], perf),
            balance=Balance.from_dict(cfg['balance']),
            store=store
        )
        return Context(
            config=cfg,
            exchange=exchange,
            feed=feed,
            record=record
        )
