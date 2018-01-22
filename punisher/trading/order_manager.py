import datetime
from copy import deepcopy

import ccxt

from punisher.portfolio.asset import Asset
from punisher.portfolio.balance import BalanceType

from .errors import handle_ordering_exception
from .order import Order
from .order import OrderType, OrderStatus


def build_limit_buy_order(exchange, asset, quantity, price):
    return Order(
        exchange_id=exchange.id,
        asset=asset,
        price=price,
        quantity=quantity,
        order_type=OrderType.LIMIT_BUY,
    )

def build_limit_sell_order(exchange, asset, quantity, price):
    return Order(
        exchange_id=exchange.id,
        asset=asset,
        price=price,
        quantity=quantity,
        order_type=OrderType.LIMIT_SELL,
    )

def build_market_buy_order(exchange, asset, quantity):
    return Order(
        exchange_id=exchange.id,
        asset=asset,
        price=None,
        quantity=quantity,
        order_type=OrderType.MARKET_BUY,
    )

def build_market_sell_order(exchange, asset, quantity):
    return Order(
        exchange_id=exchange.id,
        asset=asset,
        price=None,
        quantity=quantity,
        order_type=OrderType.MARKET_SELL,
    )

def get_order(exchange, ex_order_id, asset):
    return exchange.fetch_order(ex_order_id, asset)

def get_orders(exchange, ex_order_ids, assets):
    ex_orders = []
    if not isinstance(assets, list):
        asset = deepcopy(assets)
        assets = [asset for i in range(len(ex_order_ids))]
    for ex_order_id, asset in zip(ex_order_ids, assets):
        ex_order = get_order(exchange, ex_order_id, asset)
        ex_orders.append(ex_order)
    return ex_orders

def process_orders(exchange, orders):
    filled_orders = []

    # sync OPEN orders (to check if FILLED)
    open_orders = get_open_orders(orders)
    for oo in open_orders:
        ex_order = get_order(exchange, oo.exchange_order_id, oo.asset)
        sync_order_with_exchange(oo, ex_order)
    filled_orders.extend(get_filled_orders(open_orders))

    # retry FAILED orders (if attempts < RETRY_LIMIT)
    failed_orders = get_failed_orders(orders, retry_limit=3)
    retried_orders = place_orders(exchange, failed_orders)
    filled_orders.extend(get_filled_orders(retried_orders))

    # place CREATED orders
    created_orders = get_created_orders(orders)
    placed_orders = place_orders(exchange, created_orders)
    filled_orders.extend(get_filled_orders(placed_orders))

    assert_no_duplicates(filled_orders)

    return filled_orders

def assert_no_duplicates(orders):
    keys = set()
    for o in orders:
        if o.id in keys:
            raise Exception("duplicate found", o.id, orders)
        keys.add(o.id)

def place_order(exchange, order):
    """Submits order to exchange"""
    try:
        if order.order_type == OrderType.LIMIT_BUY:
            ex_order = exchange.create_limit_buy_order(
                order.asset, order.quantity, order.price)
        elif order.order_type == OrderType.LIMIT_SELL:
            ex_order = exchange.create_limit_sell_order(
                order.asset, order.quantity, order.price)
        elif order.order_type == OrderType.MARKET_BUY:
            ex_order = exchange.create_market_buy_order(
                order.asset, order.quantity)
        elif order.order_type == OrderType.MARKET_SELL:
            ex_order = exchange.create_market_sell_order(
                order.asset, order.quantity)
        else:
            raise Exception("Order type {:s} not supported".format(
                order.order_type.name))
        sync_order_with_exchange(order, ex_order)

    # TODO: Create Parent Exception Class and Catch a bunch of errors
    except ccxt.errors.InsufficientFunds as ex:
        error = handle_ordering_exception(ex)
        order.error = error
        order.status = OrderStatus.FAILED
        print("Order Failed", order)

    order.attempts += 1
    return order

def sync_order_with_exchange(order, ex_order):
    order.exchange_order_id = ex_order.ex_order_id
    order.opened_time = ex_order.opened_time
    order.filled_time = ex_order.filled_time
    order.canceled_time = ex_order.canceled_time
    order.status = ex_order.status
    order.filled_quantity = ex_order.filled_quantity
    order.price = ex_order.price
    order.fee = ex_order.fee
    order.trades = ex_order.trades

def place_orders(exchange, orders):
    placed = []
    for order in orders:
        placed_order = place_order(exchange, order)
        placed.append(placed_order)
    return placed

def cancel_order(exchange, ex_order_id):
    cancel_response = exchange.cancel_order(
        order_id=ex_order_id)
    return cancel_response

def cancel_orders(exchange, orders):
    cancel_responses = []
    for order in orders:
        resp = cancel_order(exchange, order.exchange_order_id)
        cancel_responses.append(resp)
    return cancel_responses


def get_created_orders(orders):
    return get_orders_by_types(orders, [OrderStatus.CREATED])

def get_open_orders(orders):
    return get_orders_by_types(orders, [OrderStatus.OPEN])

def get_filled_orders(orders):
    return get_orders_by_types(orders, [OrderStatus.FILLED])

def get_canceled_orders(orders):
    return get_orders_by_types(orders, [OrderStatus.CANCELED])

def get_failed_orders(orders, retry_limit=0):
    orders = get_orders_by_types(orders, [OrderStatus.FAILED])
    failed_orders = []
    for order in orders:
        if order.attempts <= retry_limit:
            failed_orders.append(order)
    return failed_orders

def get_orders_by_types(orders, order_types):
    results = []
    for order in orders:
        if order.status in order_types:
            results.append(order)
    return results

def get_order_by_ex_order_id(orders, ex_order_id):
    for order in orders:
        if order.exchange_order_id == ex_order_id:
            return order
    return None
