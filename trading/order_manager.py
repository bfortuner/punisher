from .order import Order
from .order import OrderType, OrderStatus


def get_pending_orders(orders_dict):
    pending_orders = []
    for _, order in orders_dict.items():
        if order.get_status() in [OrderStatus.NEW, OrderStatus.ATTEMPED]:
            pending_orders.append(order)
    return pending_orders

def get_order_by_exchange_id(ex_order_id, orders_dict):
    for _, order in orders_dict.items():
        if order.exchange_order_id == ex_order_id:
            return order
    return None
