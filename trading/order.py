import copy
import json
import uuid
from datetime import datetime
from enum import Enum, unique

from portfolio.asset import Asset
from utils.dates import str_to_date, date_to_str
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

    def __init__(self, exchange_id, asset, price, quantity, order_type):
        self.id = self.make_id()
        self.exchange_id = exchange_id
        self.exchange_order_id = None
        self.asset = asset
        self.price = price
        self.quantity = quantity
        self.filled = 0 # ratio or quantity?
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
        self.order_type = order_type
        return self.order_type

    def set_status(self, status):
        assert status in OrderStatus
        self.status = status

    def to_dict(self):
        d = {
            name: getattr(self, name)
            for name in self.__slots__
        }
        d['asset'] = self.asset.to_dict()
        d['status'] = self.status.name
        d['order_type'] = self.order_type.name
        d['created_time'] = date_to_str(self.created_time)
        d['opened_time'] = date_to_str(self.opened_time)
        d['filled_time'] = date_to_str(self.filled_time)
        d['canceled_time'] = date_to_str(self.canceled_time)
        return d

    @classmethod
    def from_dict(self, d):
        order = Order(
            exchange_id=d['exchange_id'],
            asset=Asset(d['asset']['base'], d['asset']['quote']),
            price=d['price'],
            quantity=d['quantity'],
            order_type=OrderType[d['order_type']],
        )
        order.id = d['id']
        order.exchange_order_id = d['exchange_order_id']
        order.filled = d['filled']
        order.status = OrderStatus[d['status']]
        order.created_time = str_to_date(d['created_time'])
        order.opened_time = str_to_date(d['opened_time'])
        order.filled_time = str_to_date(d['filled_time'])
        order.canceled_time = str_to_date(d['canceled_time'])
        order.retries = d['retries']
        return order

    def to_json(self):
        dct = self.to_dict()
        return json.dumps(dct, cls=EnumEncoder, indent=4)

    @classmethod
    def from_json(self, json_str):
        dct = json.loads(json_str)
        return self.from_dict(dct)

    def __repr__(self):
        return self.to_json()
