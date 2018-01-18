import copy
import json
import uuid
from datetime import datetime
from enum import Enum, unique

from punisher.portfolio.asset import Asset
from punisher.utils.dates import str_to_date, date_to_str
from punisher.trading.coins import get_symbol
from punisher.utils.encoders import EnumEncoder


@unique
class OrderStatus(Enum):
    CREATED = "Order not yet submitted to exchange"
    OPEN = "Order created on exchange, but not completely filled"
    FILLED = "Order completely filled on exchange"
    CANCELED = "Order canceled by user"
    FAILED = "Order failed/rejected by exchange. Will retry"
    KILLED = "Order rejected by exchange. Will not retry"

    def __repr__(self):
        return str(self.name)


@unique
class OrderType(Enum):
    LIMIT_BUY = {'type':'limit', 'side':'buy', 'desc':''}
    LIMIT_SELL = {'type':'limit', 'side':'sell', 'desc':''}
    MARKET_BUY = {'type':'market', 'side':'buy', 'desc':''}
    MARKET_SELL = {'type':'market', 'side':'sell', 'desc':''}
    STOP_LIMIT_BUY = 4
    STOP_LIMIT_SELL = 5

    @classmethod
    def from_type_side(self, type_, side):
        # TODO: Add more order types
        order_type_map = {
            'limit_buy': OrderType.LIMIT_BUY,
            'limit_sell': OrderType.LIMIT_SELL,
            'market_buy': OrderType.MARKET_BUY,
            'market_sell': OrderType.MARKET_SELL,
        }
        key = type_.lower() + '_' + side.lower()
        return order_type_map[key]

    @classmethod
    def buy_types(self):
        return set([
            OrderType.LIMIT_BUY,
            OrderType.MARKET_BUY,
            OrderType.STOP_LIMIT_BUY
        ])

    @classmethod
    def sell_types(self):
        return set([
            OrderType.LIMIT_SELL,
            OrderType.MARKET_SELL,
            OrderType.STOP_LIMIT_SELL
        ])

    @property
    def type(self):
        return self.value['type']

    @property
    def side(self):
        return self.value['side']

    def is_buy(self):
        return self in self.buy_types()

    def is_sell(self):
        return self in self.sell_types()

    def __repr__(self):
        return str(self.name)


class Order():
    __slots__ = [
        "id", "exchange_id", "exchange_order_id", "asset", "price",
        "quantity", "filled_quantity", "order_type", "status",
        "created_time", "opened_time", "filled_time", "canceled_time",
        "fee", "retries", "trades"
    ]

    def __init__(self, exchange_id, asset, price, quantity,
                 order_type, order_id=None, exchange_order_id=None):
        self.id = order_id
        self.exchange_id = exchange_id
        self.exchange_order_id = exchange_order_id
        self.asset = asset
        self.price = price
        self.quantity = quantity # e.g. # of bitcoins
        self.filled_quantity = 0.0
        self.order_type = self.set_order_type(order_type)
        self.status = OrderStatus.CREATED
        self.created_time = None
        self.opened_time = None
        self.filled_time = None
        self.canceled_time = None
        self.fee = {}
        self.retries = 0
        self.trades = []

    @classmethod
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
        dct = {
            name: getattr(self, name)
            for name in self.__slots__
        }
        del dct['asset']
        dct['symbol'] = self.asset.symbol
        dct['status'] = self.status.name
        dct['order_type'] = self.order_type.name
        dct['created_time'] = date_to_str(self.created_time)
        dct['opened_time'] = date_to_str(self.opened_time)
        dct['filled_time'] = date_to_str(self.filled_time)
        dct['canceled_time'] = date_to_str(self.canceled_time)
        return dct

    @classmethod
    def from_dict(self, d):
        order = Order(
            exchange_id=d['exchange_id'],
            asset=Asset.from_symbol(d['symbol']),
            price=d['price'],
            quantity=d['quantity'],
            order_type=OrderType[d['order_type']],
        )
        order.id = d.get('id', order.id)
        order.exchange_order_id = d.get('exchange_order_id')
        order.filled_quantity = d.get('filled_quantity', 0)
        order.status = OrderStatus[d.get('status', OrderStatus.CREATED.name)]
        order.created_time = str_to_date(d.get('created_time'))
        order.opened_time = str_to_date(d.get('opened_time'))
        order.filled_time = str_to_date(d.get('filled_time'))
        order.canceled_time = str_to_date(d.get('canceled_time'))
        order.retries = d.get('retries', 0)
        order.fee = d.get('fee', {})
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

def buy_order_types():
    return [OrderType.LIMIT_BUY,
            OrderType.MARKET_BUY,
            OrderType.STOP_LIMIT_BUY]

def sell_order_types():
    return [OrderType.LIMIT_SELL,
            OrderType.MARKET_SELL,
            OrderType.STOP_LIMIT_SELL]
