import os
import time
import logging

from datetime import datetime, timedelta
from enum import Enum, unique
from copy import deepcopy

import punisher.config as cfg
import punisher.constants as c
from punisher.data.store import DATA_STORES, FILE_STORE
from punisher.data.feed import EXCHANGE_FEED, CSV_FEED
from punisher.data.feed import load_feed
from punisher.utils.dates import Timeframe
from punisher.portfolio.portfolio import Portfolio
from punisher.portfolio.asset import Asset
from punisher.portfolio.balance import Balance, BalanceType
from punisher.portfolio.performance import PerformanceTracker
from punisher.exchanges.exchange import load_exchange, CCXTExchange
from punisher.utils.dates import str_to_date
from punisher.utils.logger import get_logger

from . import order_manager
from .record import Record


class Context():
    def __init__(self, exchange, feed, record):
        self.exchange = exchange
        self.feed = feed
        self.record = record
        self.logger = self.init_logger(record)

    def init_logger(self, record):
        root = os.path.join(cfg.DATA_DIR, record.config['experiment'])
        return get_logger(
            fpath=root,
            logger_name='progress',
            ch_log_level=logging.INFO
        )

    @classmethod
    def from_config(self, config):
        root = os.path.join(cfg.DATA_DIR, config['experiment'])
        store = DATA_STORES[cfg.DATA_STORE](root)
        feed = load_feed(
            name=config['feed']['name'],
            fpath=config['feed']['fpath'],
            assets=[Asset.from_symbol(a) for a in config['feed']['symbols']],
            timeframe=Timeframe[config['feed']['timeframe']],
            start=str_to_date(config['feed'].get('start')),
            end=str_to_date(config['feed'].get('end')),
        )
        feed.initialize(exchange)
        perf = PerformanceTracker(
            starting_cash=config['starting_cash'],
            timeframe=Timeframe[config['feed']['timeframe']],
            store=store
        )
        record = Record(
            config=cfg,
            portfolio=Portfolio(config['starting_cash'], perf),
            balance=Balance.from_dict(config['balance']),
            store=store
        )
        exchange = load_exchange(
            config['exchange']['exchange_id'],
            cfg=config['exchange']
        )
        logger = get_logger(
            fpath=root,
            logger_name='progress',
            ch_log_level=logging.INFO
        )

        return Context(
            exchange=exchange,
            feed=feed,
            record=record,
            logger=logger
        )


def get_default_backtest_config(name, symbols):
    name = name + '_backtest'
    root = os.path.join(cfg.DATA_DIR, name)
    return {
        'experiment': name,
        'cash_asset': c.BTC,
        'starting_cash': 1.0,
        'store': cfg.DATA_STORE,
        'feed': CSV_FEED,
        'balance': c.DEFAULT_BALANCE,
        'feed': {
            'name': name,
            'root': root,
            'symbols': symbols,
            'start': '2018-01-01T00:00:00',
            'timeframe': Timeframe.THIRTY_MIN.name,
            'fpath': None
        },
        'exchange': {
            'id': c.PAPER
        }
    }

def get_default_simulation_config(name, symbols):
    name = name + '_sim'
    root = os.path.join(cfg.DATA_DIR, name)
    return {
        'experiment': name,
        'cash_asset': c.BTC,
        'starting_cash': 1.0,
        'store': cfg.DATA_STORE,
        'feed': EXCHANGE_FEED,
        'balance': c.DEFAULT_BALANCE,
        'feed': {
            'name': name,
            'root': root,
            'symbols': symbols,
            'start': datetime.utcnow().isoformat(),
            'timeframe': Timeframe.ONE_MIN.name,
            'fpath': None
        },
        'exchange': {
            'id': c.PAPER,
        }
    }

def get_default_live_config(name, symbols):
    return {}
