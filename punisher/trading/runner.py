import os
import time
from enum import Enum, unique

import punisher.config as cfg
import punisher.constants as c
from punisher.data.store import DATA_STORES
from punisher.portfolio.portfolio import Portfolio
from punisher.trading import order_manager
from punisher.exchanges.exchange import load_exchange

from .context import Context
from .record import Record


@unique
class TradeMode(Enum):
    BACKTEST = 'historical data, fake orders'
    SIMULATE = 'live data, fake orders'
    LIVE = 'live data, live orders'


def get_latest_prices(orders, row, ex_id):
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
    record.save()
    ctx = Context(
        exchange=exchange,
        feed=feed,
        record=record
    )

    row = feed.next()
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
        newly_filled_orders = order_manager.process_orders(
            exchange, record.orders.values())

        # Update latest prices of positions
        latest_prices = get_latest_prices(orders, row, exchange.id)
        # Portfolio needs to know about new filled orders
        portfolio.update(row.get('utc'), newly_filled_orders, latest_prices)

        # Update Virtual Balance (exchange balance left alone)
        for order in newly_filled_orders:
            balance.update_by_order(order.asset, order.quantity,
                                    order.price, order.order_type)
            print("Equal?", record.balance == exchange.fetch_balance())

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
    record.save()
    ctx = Context(
        exchange=exchange,
        feed=feed,
        record=record
    )

    while True:
        row = feed.next()

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
            newly_filled_orders = order_manager.process_orders(
                exchange, record.orders.values())

            # Update latest prices of positions
            latest_prices = get_latest_prices(orders, row, exchange.id)
            # Portfolio needs to know about new filled orders
            portfolio.update(row.get('utc'), newly_filled_orders, latest_prices)

            # Update Virtual Balance (exchange balance left alone)
            for order in newly_filled_orders:
                balance.update_by_order(order.asset, order.quantity,
                                        order.price, order.order_type)
                print("Equal?", record.balance == exchange.fetch_balance())

            record.save()

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
    record.save()
    ctx = Context(
        exchange=exchange,
        feed=feed,
        record=record
    )

    while True:
        row = feed.next()

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
            newly_filled_orders = order_manager.process_orders(
                exchange, record.orders.values())

            # Update latest prices of positions
            latest_prices = get_latest_prices(orders, row, exchange.id)
            # Portfolio needs to know about new filled orders
            portfolio.update(row.get('utc'), newly_filled_orders, latest_prices)

            # Update Virtual Balance (exchange balance left alone)
            for order in newly_filled_orders:
                balance.update_by_order(order.asset, order.quantity,
                                        order.price, order.order_type)
                print("Equal?", record.balance == exchange.fetch_balance())

            record.save()

        time.sleep(30)

    return record
