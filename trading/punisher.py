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


def punish(context, strategy):
    print("Punishing ...")
    record = context.record
    feed = context.feed
    row = feed.next()
    while True:
        row = feed.next()
        if row is not None:
            print("Timestep", row['time_utc'], "Price", row['close'])
            orders = strategy.process(row, context)
        order_manager.place_orders(context.exchange, orders)
        time.sleep(.1)
        record.save()
    return record
