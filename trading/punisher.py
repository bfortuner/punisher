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


def punish(ctx, strategy):
    print("Punishing ...")
    print(ctx.config)
    record = ctx.record
    feed = ctx.feed
    row = feed.next()

    while True:
        row = feed.next()
        if row is not None:
            orders = strategy.process(row, ctx)

        # We assume everything is filled for now
        filled_orders = order_manager.place_orders(ctx.exchange, orders)

        # Portolio needs to know about new filled orders
        ctx.record.portfolio.update_positions(filled_orders)

        # Record needs to know about new orders, Portolio
        for order in filled_orders:
            ctx.record.orders[order.id] = order

        # Update Balance
        # We're not updating the virtual balance, only the exchange
        # which is OK until we have a multi-exchange algo
        record.balance = ctx.exchange.balance

        # Save to file
        record.save()
        time.sleep(2)

    return record
