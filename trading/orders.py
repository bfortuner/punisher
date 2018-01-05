from datetime import datetime
from enum import Enum, unique
from utils.coins import get_symbol

@unique
class OrderStatus(Enum):
    PRE_EXECUTE = 0
    OPEN = 1
    FILLED = 2
    CANCELED = 3

@unique
class OrderType(Enum):
    BUY_LIMIT = 0
    SELL_LIMIT = 1

class Order():
    def __init__(self, ex_id, coin, market, price, quantity, order_type):
        self.exchange_id = ex_id
        self.coin = coin
        self.market = market
        self.price = price
        self.quantity = quantity
        self.order_type = order_type
        self._status = OrderStatus.PRE_EXECUTE
        self.created_time = datetime.utcnow()
        self.opened_time = None
        self.filled_time = None
        self.canceled_time = None

    def get_status(self):
        return self._status

    def set_status(self, status):
        assert status in OrderStatus
        self._status = status

    def get_symbol(self):
        return get_symbol(self.coin, self.market)