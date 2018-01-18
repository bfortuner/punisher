import os
import time

import punisher.config as cfg
import punisher.constants as c

from punisher.data.store import DATA_STORES
from punisher.portfolio.portfolio import Portfolio
from punisher.trading import order_manager
from punisher.exchanges.exchange import load_exchange

from .context import Context
from .context import TradingMode
from .record import Record


def get_latest_prices(positions, row):
    # TODO: refactor this to work for multiple assets
    latest_prices = {}
    for pos in positions:
        latest_prices[pos.asset.symbol] = row['close']
    return latest_prices

def backtest(name, exchange, balance, portfolio, feed, strategy):
    '''
    name = name of your current experiment run
    '''
    # Where we will save the record
    root = os.path.join(cfg.DATA_DIR, name)

    # This can be retrieved from the user's global config
    store = DATA_STORES[cfg.DATA_STORE](root=root)

    config = {
        'experiment': name,
        'strategy': strategy.name,
    }
    record = Record(
        config=config,
        portfolio=portfolio,
        balance=balance,
        store=store
    )
    ctx = Context(
        exchange=exchange,
        feed=feed,
        record=record
    )
    feed.initialize()

    row = feed.next()
    while row is not None:

        # Call strategy
        # {
        #   'orders': [Order(), Order()]
        #   'cancel_ids': ['order_id', order_id']
        # }
        orders = strategy.process(row, ctx)

        # TODO: Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        order_manager.cancel_orders(exchange, orders['cancel_ids'])

        # Returns both FILLED and PENDING orders
        # TODO: Order manager handles mapping from Exchange JSON
        # Particularly order types like CLOSED --> FILLED,
        # And OPEN vs PENDING <-- check the 'quantity' vs 'filled' amounts
        orders = order_manager.place_orders(exchange, orders['orders'])
        filled_orders = order_manager.get_filled_orders(orders)

        # Portfolio needs to know about new filled orders
        portfolio.update(filled_orders)

        # Getting the latest prices for each of our positions
        latest_prices = get_latest_prices(portfolio.positions, row)
        portfolio.update_position_prices(latest_prices)

        # Record needs to know about all new orders
        for order in orders:
            record.orders[order.id] = order

        # Update Virtual Balance (exchange balance left alone)
        for order in filled_orders:
            balance.update_by_order(order)
            print("Equal?", record.balance == exchange.fetch_balance())

        record.save()
        row = feed.next()

    return record


def simulate(name, exchange, balance, portfolio, feed, strategy):
    '''
    exp_name = name of your current experiment (multiple runs per strategy)
    '''
    # Where we will save the record
    root = os.path.join(cfg.DATA_DIR, name)

    # This can be retrieved from the user's global config
    store = DATA_STORES[cfg.DATA_STORE](root=root)

    config = {
        'experiment': name,
        'strategy': strategy.name,
    }
    record = Record(
        config=config,
        portfolio=portfolio,
        balance=balance,
        store=store
    )
    ctx = Context(
        exchange=exchange,
        feed=feed,
        record=record
    )
    feed.initialize()

    while True:
        row = feed.next()

        if row is not None:
            orders = strategy.process(row, ctx)

            # TODO: Cancelling orders
            # should we auto-cancel any outstanding orders
            # or should we leave this decision up to the Strategy?
            order_manager.cancel_orders(exchange, orders['cancel_ids'])

            # Returns both FILLED and PENDING orders
            # TODO: Order manager handles mapping from Exchange JSON
            # Particularly order types like CLOSED --> FILLED,
            # And OPEN vs PENDING <-- check the 'quantity' vs 'filled' amounts
            orders = order_manager.place_orders(exchange, orders['orders'])
            filled_orders = order_manager.get_filled_orders(orders)

            # Portfolio needs to know about new filled orders
            portfolio.update(filled_orders)

            # Getting the latest prices for each of our positions
            latest_prices = get_latest_prices(portfolio.positions, row)
            portfolio.update_position_prices(latest_prices)

            # Record needs to know about all new orders
            for order in orders:
                record.orders[order.id] = order

            # Update Virtual Balance
            # exchange balance may be impacted by external trading
            for order in filled_orders:
                balance.update_by_order(order)

            record.save()

        time.sleep(30)

    return record
