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
        orders = strategy.process(row, ctx)

        # Record needs to know about all new orders
        for order in orders['orders']:
            record.orders[order.id] = order

        # TODO: Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        # order_manager.cancel_orders(exchange, orders['cancel_ids'])

        # Place new orders, retry failed orders, sync existing orders
        newly_filled_orders = order_manager.process_orders(
            exchange, record.orders.values())

        # Portfolio needs to know about new filled orders
        portfolio.update(newly_filled_orders)

        # Update latest prices of positions
        latest_prices = get_latest_prices(portfolio.positions, row)
        portfolio.update_position_prices(latest_prices)

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
            print("ORDERS", orders)
            # Record needs to know about all new orders
            for order in orders['orders']:
                record.orders[order.id] = order

            # TODO: Cancelling orders
            # should we auto-cancel any outstanding orders
            # or should we leave this decision up to the Strategy?
            # order_manager.cancel_orders(exchange, orders['cancel_ids'])

            # Place new orders, retry failed orders, sync existing orders
            newly_filled_orders = order_manager.process_orders(
                exchange, record.orders.values())

            # Portfolio needs to know about new filled orders
            portfolio.update(newly_filled_orders)

            # Update latest prices of positions
            latest_prices = get_latest_prices(portfolio.positions, row)
            portfolio.update_position_prices(latest_prices)

            # Update Virtual Balance (exchange balance left alone)
            for order in newly_filled_orders:
                balance.update_by_order(order.asset, order.quantity,
                                        order.price, order.order_type)
                print("Equal?", record.balance == exchange.fetch_balance())

            record.save()

        time.sleep(60)

    return record


def live(name, exchange, balance, portfolio, feed, strategy):
    print("LIVE TRADING DUDE!!!!")
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

            # Record needs to know about all new orders
            for order in orders['orders']:
                record.orders[order.id] = order

            # TODO: Cancelling orders
            # should we auto-cancel any outstanding orders
            # or should we leave this decision up to the Strategy?
            # order_manager.cancel_orders(exchange, orders['cancel_ids'])

            # Place new orders, retry failed orders, sync existing orders
            newly_filled_orders = order_manager.process_orders(
                exchange, record.orders.values())

            # Portfolio needs to know about new filled orders
            portfolio.update(newly_filled_orders)

            # Update latest prices of positions
            latest_prices = get_latest_prices(portfolio.positions, row)
            portfolio.update_position_prices(latest_prices)

            # Update Virtual Balance (exchange balance left alone)
            for order in newly_filled_orders:
                balance.update_by_order(order.asset, order.quantity,
                                        order.price, order.order_type)
                print("Equal?", record.balance == exchange.fetch_balance())

            record.save()

        time.sleep(60)

    return record
