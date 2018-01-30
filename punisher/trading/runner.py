import os
import time
from enum import Enum, unique
from datetime import datetime, timedelta

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


def get_latest_prices(symbols_traded, row, ex_id):
    """
    Helper method to get latest prices for each order
    from the last data row.
    - orders : all Order objects
    - row : last data row
    - ex_id: exchange id
    """
    # TODO: ensure this works for multi exchange
    latest_prices = {}
    for symbol in symbols_traded:
        latest_prices[symbol] = row.get('close', symbol, ex_id)
    return latest_prices

def get_symbols_traded(orders, positions):
    symbols_traded = [order.asset.symbol for order in orders]
    symbols_traded.extend(
        [position.asset.symbol for position in positions])
    return set(symbols_traded)


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
        balance=portfolio.balance,
        store=store
    )
    ctx = Context(
        exchange=exchange,
        feed=feed,
        record=record
    )

    row = feed.next()
    last_port_update_time = row.get('utc') - feed.timeframe.delta
    orders = []
    record.save()
    while row is not None:

        output = strategy.process(row, ctx)
        # Add any new orders from strategy output
        new_orders = output['new_orders']
        cancel_ids = output['cancel_ids']

        orders.extend(new_orders)
        # TODO: Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        # How do we confirm the order has been cancelled by the exchange?
        # order_manager.cancel_orders(exchange, cancel_ids)

        updated_orders = order_manager.process_orders(
            exchange, portfolio.balance, orders)

        # Get the symbols traded in this strategy
        symbols_traded = get_symbols_traded(
                orders, portfolio.positions)

        # Update latest prices of positions
        latest_prices = get_latest_prices(
            symbols_traded, row, exchange.id)

        # Portfolio needs to know about new trades and latest prices
        portfolio.update(
            last_port_update_time, row.get('utc') , updated_orders, latest_prices)

        last_port_update_time = row.get('utc')

        # Update record with updates to orders
        for order in updated_orders:
            record.orders[order.id] = order

        # Reset open orders list to only track open/created orders
        orders = order_manager.get_open_orders(updated_orders)
        orders.extend(
            order_manager.get_created_orders(updated_orders))

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
        balance=portfolio.balance,
        store=store
    )
    ctx = Context(
        exchange=exchange,
        feed=feed,
        record=record
    )

    row = feed.next()
    last_port_update_time = datetime.utcnow()
    orders = []
    record.save()

    while True:

        if row is not None:
            output = strategy.process(row, ctx)
            # Add any new orders from strategy output
            new_orders = output['new_orders']
            cancel_ids = output['cancel_ids']

            # Add new orders to our orders list
            orders.extend(new_orders)


        # TODO: Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        # order_manager.cancel_orders(exchange, cancel_ids)

        # Place new orders, retry failed orders, sync existing orders
        updated_orders = order_manager.process_orders(
                            exchange=exchange,
                            balance=portfolio.balance,
                            open_or_new_orders=orders
                        )
        # Get the symbols traded in this strategy
        symbols_traded = get_symbols_traded(
            orders, portfolio.positions)

        # Update latest prices of positions
        latest_prices = get_latest_prices(
                symbols_traded, row, exchange.id)

        current_time = datetime.utcnow()
        # Portfolio needs to know about new trades/latest prices
        portfolio.update(
            last_port_update_time, current_time, updated_orders, latest_prices)

        # Keep updating last time we updated our portfolio
        last_port_update_time = current_time

        # Reset open orders list to only track open/created orders
        orders = order_manager.get_open_orders(updated_orders)
        orders.extend(
            order_manager.get_created_orders(updated_orders))

        # Update record with updates to orders
        for order in updated_orders:
            record.orders[order.id] = order

        record.save()
        row = feed.next()

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
        balance=portfolio.balance,
        store=store
    )
    ctx = Context(
        exchange=exchange,
        feed=feed,
        record=record
    )

    row = feed.next()
    last_port_update_time = datetime.utcnow()
    orders = []
    record.save()

    while True:

        if row is not None:
            output = strategy.process(row, ctx)
            # Add any new orders from strategy output
            new_orders = output['new_orders']
            cancel_ids = output['cancel_ids']

            # Add new orders to our orders list
            orders.extend(new_orders)


        # TODO: Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        # order_manager.cancel_orders(exchange, cancel_ids)

        # Place new orders, retry failed orders, sync existing orders
        updated_orders = order_manager.process_orders(
                            exchange=exchange,
                            balance=portfolio.balance,
                            open_or_new_orders=orders
                        )
        # Get the symbols traded in this strategy
        symbols_traded = get_symbols_traded(
            orders, portfolio.positions)

        # Update latest prices of positions
        latest_prices = get_latest_prices(
                symbols_traded, row, exchange.id)

        current_time = datetime.utcnow()
        # Portfolio needs to know about new trades/latest prices
        portfolio.update(
            last_port_update_time, current_time, updated_orders, latest_prices)

        # Keep updating last time we updated our portfolio
        last_port_update_time = current_time

        # Reset open orders list to only track open/created orders
        orders = order_manager.get_open_orders(updated_orders)
        orders.extend(
            order_manager.get_created_orders(updated_orders))

        # Update record with updates to orders
        for order in updated_orders:
            record.orders[order.id] = order

        record.save()
        row = feed.next()

    return record
