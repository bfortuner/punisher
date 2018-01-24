import os
import time
from enum import Enum, unique

import punisher.config as cfg
import punisher.constants as c
from punisher.data.store import DATA_STORES
from punisher.exchanges import load_exchange
from punisher.portfolio.portfolio import Portfolio
from punisher.trading import order_manager

from .context import Context
from .record import Record


@unique
class TradeMode(Enum):
    BACKTEST = 'historical data, fake orders'
    SIMULATE = 'live data, fake orders'
    LIVE = 'live data, live orders'


def get_latest_prices(orders, row, ex_id):
    """
    Helper method to get latest prices for each order from the last data row.
    - orders : all Order objects
    - row : last data row
    - ex_id: exchange id
    """
    # TODO: ensure this works for multi exchange
    latest_prices = {}
    for order in orders:
        symbol = order.asset.symbol
        latest_prices[symbol] = row.get('close', symbol, ex_id)
    return latest_prices


def backtest(name, exchange, balance, portfolio, feed, strategy):
    '''
    :name = name of your current experiment run
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
    row = feed.next()
    portfolio.last_update_timestamp = row.get('utc')
    record.save()

    while row is not None:
        output = strategy.process(row, ctx)
        orders = output['orders']
        cancel_ids = output['cancel_ids']

        # Record needs to know about all new orders
        for order in orders:
            record.orders[order.id] = order

        # TODO: Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        # order_manager.cancel_orders(exchange, cancel_ids)

        # Place new orders, retry failed orders, sync existing orders
        # TODO: make order_manger update and return all orders
        updated_orders = order_manager.process_orders(
            exchange, record.orders.values())

        # Update latest prices of positions
        latest_prices = get_latest_prices(updated_orders, row, exchange.id)

        # Portfolio needs to know about new trades and latest prices
        portfolio.update(row.get('utc'), updated_orders, latest_prices)

        record.save()
        row = feed.next()

    return record

def simulate(name, exchange, balance, portfolio, feed, strategy):
    '''
    :name = name of your current experiment run
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
    row = feed.next()
    portfolio.last_update_timestamp = row.get('utc')
    orders = []
    record.save()

    # TODO:
    # Order manager update orders every timestep
    #   - ensure we are not losing orders when the strategy returns new orders
    #        - like make sure that they are part of all existing orders


    while True:

        if row is not None:
            output = strategy.process(row, ctx)
            orders = output['orders']
            cancel_ids = output['cancel_ids']

            # Record needs to know about all new orders
            for order in orders:
                record.orders[order.id] = order

            # TODO: Cancelling orders
            # should we auto-cancel any outstanding orders
            # or should we leave this decision up to the Strategy?
            # order_manager.cancel_orders(exchange, cancel_ids)

            # Place new orders, retry failed orders, sync existing orders
            # TODO: DECIDE IF THIS SHOULD HAPPEN EVERY ROUND
            updated_orders = order_manager.process_orders(
                exchange, record.orders.values())

            # Update latest prices of positions
            latest_prices = get_latest_prices(updated_orders, row, exchange.id)

            # Portfolio needs to know about new trades and latest prices
            portfolio.update(row.get('utc'), updated_orders, latest_prices)

            record.save()

        row = feed.next()
        time.sleep(30)

    return record

def live(name, exchange, balance, portfolio, feed, strategy):
    '''
    :name = name of your current experiment run
    '''
    print("LIVE TRADING! My, man!")

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

    row = feed.next()
    portfolio.last_update_timestamp = row.get('utc')
    record.save()

    # TODO: Same as above

    while True:

        if row is not None:
            output = strategy.process(row, ctx)
            orders = output['orders']
            cancel_ids = output['cancel_ids']

            # Record needs to know about all new orders
            for order in orders:
                record.orders[order.id] = order

            # TODO: Cancelling orders
            # should we auto-cancel any outstanding orders
            # or should we leave this decision up to the Strategy?
            # order_manager.cancel_orders(exchange, cancel_ids)

            # Place new orders, retry failed orders, sync existing orders
            updated_orders = order_manager.process_orders(
                exchange, record.orders.values())

            # Update latest prices of positions
            latest_prices = get_latest_prices(updated_orders, row, exchange.id)

            # Portfolio needs to know about new trades and latest prices
            portfolio.update(row.get('utc'), updated_orders, latest_prices)

            record.save()

        row = feed.next()
        time.sleep(30)

    return record
