import os
import time
from enum import Enum, unique

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

from punisher.trading import order_manager
from punisher.trading.record import Record
from punisher.exchanges.exchange import load_exchange

from punisher.utils.dates import str_to_date

"""

GIST HERE: https://gist.github.com/bfortuner/ed1d0ffcc328695f9b25d3732dcb9d7d

In all cases, user can leave parameter as None
And we lookup a sensible default

USER EXPERIENCE ------------------

balance = Balance(
    cash_currency=c.BTC,
    starting_cash=1.0
)
portfolio = Portfolio(
    starting_cash=balance.starting_cash,
    perf_tracker=None, # option to override, otherwise default
    positions=None # option to override with existing positions
)
feed = CSVDataFeed(
    fpath=feed_fpath,
    start=None, # Usually None for backtest, but its possible to filter the csv
    end=None
)
strategy = MyStrategy()

backtest(balance, portfolio, feed, strategy)


INSIDE punisher.py -----------------------

def backtest(run_name, balance, portfolio, feed, strategy):
    '''
    run_name = name of your current experiment (multiple runs per strategy)
    '''

    # Where we will save the record
    root = os.path.join(proj_cfg.DATA_DIR, run_name)

    # We don't need the exchange from the user since
    # it's a backtest. We can initialize it inside the method
    # It needs to take a balance parameter, however
    exchange = load_exchange(c.PAPER, balance)

    # This can be retrieved from the user's global config
    store = DATA_STORES[cfg['store']](root=root)

    config = {'experiment': run_name, 'strategy': strategy.name}
    record = Record(
        config=config
        portfolio=portfolio,
        balance=balance,
        store=store
    )
    record.initialize()

    ctx = Context(
        config=config,
        exchange=exchange,
        feed=feed,
        record=record
    )

    while True:
        row = feed.next()
        if row is not None:
            orders = strategy.process(row, ctx)

        # TODO: Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        order_manager.cancel_orders(orders['cancel_ids'])

        # Returns both FILLED and PENDING orders
        # TODO: Order manager handles mapping from Exchange JSON
        # Paricularly order types like CLOSED --> FILLED,
        # And OPEN vs PENDING <-- check the 'quantity' vs 'filled' amounts
        orders = order_manager.place_orders(exchange, orders)
        filled_orders = order_manager.get_filled_orders(order)

        # Portfolio only needs to know about new FILLED orders
        record.portfolio.update(filled_orders)

        # Record needs to know about ALL new orders (open/filled)
        for order in orders:
            record.orders[order.id] = order

        # TODO: Update Balance
        # We're not updating the virtual balance, only the exchange
        # which is OK until we have a multi-exchange algo
        # But this also means, for live trading, we can't separate
        # fund from Algo to Algo.
        record.balance = exchange.balance

        # Save to file
        record.save()

        # How do we toggle this for backtesting vs live testing
        # and simulated trading? Should we have separate methods?
        # One for backtesting, one for paper trading, one for Live?
        # We construct the context INSIDE the method, not outside
        # Each method has two entry points: config-based, parameter-based
        time.sleep(2)

    return record

"""


def punish(ctx, strategy):
    print("Punishing ...")
    print(ctx.config)

    # Should EVERYTHING live in the Context?
    record = ctx.record
    feed = ctx.feed
    row = feed.next()

    while True:
        row = feed.next()
        if row is not None:
            orders = strategy.process(row, ctx)

        # TODO: Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        # order_manager.cancel_orders(orders['cancel_ids'])

        # Returns both FILLED and PENDING orders
        # TODO: Order manager handles mapping from Exchange JSON
        # Paricularly order types like CLOSED --> FILLED,
        # And OPEN vs PENDING <-- check the 'quantity' vs 'filled' amounts
        orders = order_manager.place_orders(ctx.exchange, orders)

        # Record needs to know about ALL new orders (open/filled)
        for order in orders:
            ctx.record.orders[order.id] = order

        # Portfolio only needs to know about new FILLED orders
        filled_orders = order_manager.get_filled_orders(orders)
        record.portfolio.update(filled_orders)

        # TODO: Update Balance
        # We're not updating the virtual balance, only the exchange
        # which is OK until we have a multi-exchange algo
        # But this also means, for live trading, we can't separate
        # fund from Algo to Algo.
        record.balance = ctx.exchange.balance

        # Save to file
        record.save()

        # How do we toggle this for backtesting vs live testing
        # and simulated trading? Should we have separate methods?
        # One for backtesting, one for paper trading, one for Live?
        # We construct the context INSIDE the method, not outside
        # Each method has two entry points: config-based, parameter-based
        time.sleep(2)

    return record
