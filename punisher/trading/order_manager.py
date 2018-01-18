import datetime
from copy import deepcopy

from punisher.portfolio.asset import Asset
from punisher.portfolio.balance import BalanceType

from .order import Order
from .order import OrderType, OrderStatus


def build_limit_buy_order(exchange, asset, quantity, price):
    order = Order(
        exchange_id=exchange.id,
        asset=asset,
        price=price,
        quantity=quantity,
        order_type=OrderType.LIMIT_BUY,
    )
    order.id = Order.make_id()
    order.created_time = datetime.datetime.utcnow()
    return order

def build_limit_sell_order(exchange, asset, quantity, price):
    order = Order(
        exchange_id=exchange.id,
        asset=asset,
        price=price,
        quantity=quantity,
        order_type=OrderType.LIMIT_SELL,
    )
    order.id = Order.make_id()
    order.created_time = datetime.datetime.utcnow()
    return order

def build_market_buy_order(exchange, asset, quantity):
    order = Order(
        exchange_id=exchange.id,
        asset=asset,
        price=None,
        quantity=quantity,
        order_type=OrderType.MARKET_BUY,
    )
    order.id = Order.make_id()
    order.created_time = datetime.datetime.utcnow()
    return order


def build_market_sell_order(exchange, asset, quantity):
    order = Order(
        exchange_id=exchange.id,
        asset=asset,
        price=None,
        quantity=quantity,
        order_type=OrderType.MARKET_SELL,
    )
    order.id = Order.make_id()
    order.created_time = datetime.datetime.utcnow()
    return order

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

def place_order(exchange, order):
    print("Placing Order", order)
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
    print("Exchange Response", ex_order)
    order = sync_order_with_exchange(order, ex_order)
    print("Updated order", order)
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
    return order

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

def get_pending_orders(orders):
    return get_orders_by_types(
        orders, [OrderStatus.CREATED, OrderStatus.OPEN])

def get_filled_orders(orders):
    return get_orders_by_types(orders, [OrderStatus.FILLED])

def get_canceled_orders(orders):
    return get_orders_by_types(orders, [OrderStatus.CANCELED])

def get_failed_orders(orders):
    return get_orders_by_types(orders, [OrderStatus.FAILED])

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
