import copy
import json
import uuid
from datetime import datetime
from enum import Enum, unique

from punisher.portfolio.asset import Asset
from punisher.utils.dates import str_to_date, date_to_str
from punisher.utils.encoders import EnumEncoder

@unique
class TradeSide(Enum):
    BUY = 0
    SELL = 1

    @classmethod
    def from_side(self, side):
        if side == 'buy':
            return TradeSide.BUY
        return TradeSide.SELL

    def is_buy(self):
        return self == TradeSide.BUY

    def is_sell(self):
        return self == TradeSide.SELL

class Trade:
    __slots__ = [
        "id", "exchange_id", "exchange_order_id", "asset", "price", "quantity",
        "trade_time", "fee", "side"
    ]

    def __init__(self, trade_id, exchange_id, exchange_order_id,
            asset, quantity, price, trade_time, side, fee):
        self.id = trade_id if trade_id else Trade.make_id()
        self.exchange_id = exchange_id
        self.exchange_order_id = exchange_order_id
        self.asset = asset
        self.price = price
        self.quantity = quantity
        self.trade_time = trade_time
        self.side = self.set_trade_side(side)
        self.fee = fee

    def set_trade_side(self, side):
        self.side = TradeSide.from_side(side)
        return self.side

    def to_dict(self):
        dct = {
            name: getattr(self, name)
            for name in self.__slots__
        }
        del dct['asset']
        dct['symbol'] = self.asset.symbol
        dct['trade_time'] = date_to_str(self.trade_time)
        return dct

    @classmethod
    def from_dict(self, d):
        return Trade(
            trade_id=d.get("id"),
            exchange_id=d['exchange_id'],
            exchange_order_id=d['order'],
            asset=Asset.from_symbol(d['symbol']),
            price=d['price'],
            quantity=d['amount'],
            trade_time=str_to_date(d['datetime']),
            side=TradeSide.from_side(d['side']),
            fee=d['fee']
        )

    def to_json(self):
        dct = self.to_dict()
        return json.dumps(dct, cls=EnumEncoder, indent=4)

    @classmethod
    def from_json(self, json_str):
        dct = json.loads(json_str)
        return self.from_dict(dct)

    @staticmethod
    def make_id():
        return uuid.uuid4().hex

    def __repr__(self):
        return self.to_json()
