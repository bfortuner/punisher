import copy
import json
from datetime import datetime
from enum import Enum, unique

from utils.dates import str_to_date
from utils.coins import get_symbol
from utils.general import generate_order_id
from utils.encoders import EnumEncoder


@unique
class OrderStatus(Enum):
    NEW = 0
    ATTEMPED = 1
    OPEN = 2
    FILLED = 3
    CANCELED = 4
    ERROR = 5

@unique
class OrderType(Enum):
    BUY_LIMIT = 0
    SELL_LIMIT = 1


class Order():
    def __init__(self, ex_id, coin, market, price, quantity, order_type):
        self.order_id = generate_order_id(12)
        self.exchange_order_id = None
        self.exchange_id = ex_id
        self.coin = coin
        self.market = market
        self.price = price
        self.quantity = quantity
        self.order_type = self.set_order_type(order_type)
        self.order_status = OrderStatus.NEW
        self.created_time = datetime.utcnow()
        self.opened_time = None
        self.filled_time = None
        self.canceled_time = None
        self.retries = 0

    def set_order_type(self, order_type):
        assert order_type in OrderType
        self.order_type = order_type
        return self.order_type

    def set_status(self, status):
        assert status in OrderStatus
        self.order_status = status

    def get_symbol(self):
        return get_symbol(self.coin, self.market)

    def to_json(self):
        return json.dumps(self.__dict__, cls=EnumEncoder)

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