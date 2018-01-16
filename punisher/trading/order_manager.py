from .order import Order
from .order import OrderType, OrderStatus


def build_limit_buy_order(exchange, asset, price, quantity):
    return Order(
        exchange_id=exchange.id,
        asset=asset,
        price=price,
        quantity=quantity,
        order_type=OrderType.LIMIT_BUY,
    )

def build_limit_sell_order(exchange, asset, price, quantity):
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

def get_order(exchange, ex_order_id, symbol=None):
    order_dct = exchange.fetch_order(ex_order_id, symbol)
    order = make_order_from_dct(order_dct, exchange.id)
    return order

def make_order_from_dct(dct, ex_id, order_id=None):
    return Order.from_dict({
        'id': order_id,
        'exchange_id': ex_id,
        'exchange_order_id': dct['id'],
        'asset': dct['asset'],
        'price': dct['price'],
        'quantity': dct['quantity'],
        'order_type': OrderType.from_type_side(dct['type'], dct['side']).name,
        'filled_quantity': dct['filled'],
        'status': dct['status'], # CAREFUL, may be inconsistent
        'fee': dct['fee'],
        'created_time': dct['created_time'],
        'filled_time': None,
        'opened_time': None,
        'canceled_time': None,
        'retries': 0,
    })

def get_orders(exchange, ex_order_ids, symbols=None):
    orders = []
    if symbols is None:
        symbols = [None] * len(ex_order_ids)
    for id_, sym in zip(ex_order_ids, symbols):
        order = get_order(exchange, id_, sym)
        orders.append(order)
    return orders

def place_order(exchange, order):
    if order.order_type == OrderType.LIMIT_BUY:
        res = exchange.create_limit_buy_order(
            order.asset, order.quantity, order.price)
    elif order.order_type == OrderType.LIMIT_SELL:
        res = exchange.create_limit_sell_order(
            order.asset, order.quantity, order.price)
    elif order.order_type == OrderType.MARKET_BUY:
        res = exchange.create_market_buy_order(
            order.asset, order.quantity)
    elif order.order_type == OrderType.MARKET_SELL:
        res = exchange.create_market_sell_order(
            order.asset, order.quantity)
    else:
        raise Exception("Order type {:s} not supported".format(
            order.order_type.name))
    if res is None:
        return None
    return make_order_from_dct(res, order.exchange_id, order.id)

def place_orders(exchange, orders):
    results = []
    for order in orders:
        res = None
        if exchange.fetch_balance().is_balance_sufficient(
                asset=order.asset,
                quantity=order.quantity,
                price=order.price,
                order_type=order.order_type
            ):
            res = place_order(exchange, order)
        else:
            print("Insufficient funds to place order {}, \
                    cancelling ...".format(order.id))
            order.set_status(OrderStatus.CANCELED)
        if res is not None:
            results.append(res)
    return results

def cancel_order(exchange, ex_order_id):
    res = exchange.cancel_order(
        order_id=ex_order_id)
    return res

def cancel_orders(exchange, orders):
    results = []
    for order in orders:
        res = cancel_order(order.exchange_order_id)
        results.append(res)
    return results

def get_pending_orders(orders):
    return get_orders_by_types(
        orders, [OrderStatus.CREATED, OrderStatus.OPEN])

def get_filled_orders(orders):
    # possibly add "closed" ?
    return get_orders_by_types(orders, [OrderStatus.FILLED])

def get_canceled_orders(orders):
    return get_orders_by_types(orders, [OrderStatus.CANCELED])

def get_canceled_orders(orders):
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
