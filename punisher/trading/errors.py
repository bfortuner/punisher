import json
from enum import Enum

import ccxt

from punisher.utils.encoders import EnumEncoder


class ErrorCode(Enum):
    INSUFFICIENT_FUNDS = {'desc': 'not enough funds to place order'}
    OTHER = {'desc': 'other error'}

    @property
    def desc(self):
        return self.value['desc']


class OrderingError():
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def to_dict(self):
        return {'code': self.code.name, 'msg': self.msg}

    @classmethod
    def from_dict(self, dct):
        if dct is None:
            return None
        return OrderingError(ErrorCode[dct['code']], dct['msg'])

    def __repr__(self):
        return json.dumps(self.to_dict(), cls=EnumEncoder, indent=4)


def handle_ordering_exception(ex):
    if isinstance(ex, ccxt.errors.InsufficientFunds):
        error = OrderingError(ErrorCode.INSUFFICIENT_FUNDS, ex.args[0])
    else:
        print("Some other error", type(ex), ex)
        error = OrderingError(ErrorCode.OTHER, ex.args[0])
    return error
