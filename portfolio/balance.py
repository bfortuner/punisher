import constants as c
import config as cfg
from enum import Enum, unique

DEFAULT_BALANCE = {
    c.USDT: {
        "free": cfg.DEFAULT_FUNDS,
        "used": 0.0,
        "total": cfg.DEFAULT_FUNDS
    }
}

@unique
class BalanceType(Enum):
    AVAILABLE = "free"
    USED = "used"
    TOTAL = "total"

"""Balance Helpers"""

def add_asset_to_balance(symbol, available_quantity, used_quantity, balance):
    balance[symbol] = {
        BalanceType.AVAILABLE: available_quantity,
        BalanceType.USED: used_quantity,
        BalanceType.TOTAL: available_quantity + used_quantity
    }
    return balance

def update_balance(symbol, available_quantity, used_quantity, balance):
    balance[symbol][BALANCE_TYPE.AVAILABLE] += available_quantity
    balance[symbol][BALANCE_TYPE.USED] += used_quantity
    balance[symbol][BALANCE_TYPE.TOTAL] += available_quantity + used_quantity
    return balance
