import copy
import json
from datetime import datetime
from enum import Enum, unique

from utils.dates import str_to_date
from trading.coins import get_symbol
from utils.encoders import EnumEncoder


@unique
class OrderStatus(Enum):
    NEW = "Order not yet submitted to exchange"
    OPEN = "Order successfully created on exchange"
    FILLED = "Order completely filled on exchange"
    CANCELED = "Order canceled by user"
    REJECTED = "Order rejected by exchange. Will retry"
    KILLED = "Order rejected by exchange. Will not retry"

@unique
class OrderType(Enum):
    LIMIT_BUY = 0
    LIMIT_SELL = 1
    MARKET_BUY = 2
    MARKET_SELL = 3
    STOP_LIMIT_BUY = 4
    STOP_LIMIT_SELL = 5


class Order():
    __slots__ = [
        "id", "exchange_id", "exchange_order_id", "asset", "price",
        "quantity", "filled", "order_type", "status", "created_time",
        "opened_time", "filled_time", "canceled_time", "retries"
    ]
    ORDER_FIELDS_TO_IGNORE = []

    def __init__(self, exchange_id, asset, price, quantity, order_type):
        self.id = self.make_id()
        self.exchange_id = exchange_id
        self.exchange_order_id = None
        self.asset = asset
        self.price = price
        self.quantity = quantity
        self.filled = 0
        self.order_type = self.set_order_type(order_type)
        self.status = OrderStatus.NEW
        self.created_time = datetime.utcnow()
        self.opened_time = None
        self.filled_time = None
        self.canceled_time = None
        self.retries = 0

    def make_id(self):
        return uuid.uuid4().hex

    def set_order_type(self, order_type):
        assert order_type in OrderType
        self.type = order_type
        return self.type

    def set_status(self, status):
        assert status in OrderStatus
        self.status = status

    def to_dict(self):
        dct = {name: getattr(self, name) for name in self.__slots__}
        dct['status'] = self.status.name
        dct['order_type'] = self.order_type.name
        return dct

    def from_dict(self)

    def __repr__(self):
        return str(vars(self))



def load_order_from_json(json_str):
    d = json.loads(json_str)
    order = Order(
        ex_id=d['exchange_id'],
        coin=d['coin'],
        market=d['market'],
        price=d['price'],
        quantity=d['quantity'],
        order_type=OrderType[d['order_type']],
    )
    order.order_id = d['order_id']
    order.exchange_order_id = d['exchange_order_id']
    order.order_status = OrderStatus[d['order_status']]
    order.created_time = str_to_date(d['created_time'])
    order.opened_time = str_to_date(d['opened_time'])
    order.filled_time = str_to_date(d['filled_time'])
    order.canceled_time = str_to_date(d['canceled_time'])
    order.retries = d['retries']
    return order
