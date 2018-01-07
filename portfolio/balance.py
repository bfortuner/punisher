import constants as c
import config as cfg
from enum import Enum, unique

DEFAULT_BALANCE = {
    c.USDT: {
        "free": cfg.DEFAULT_FUNDS,
        "used": 0,
        "total": cfg.DEFAULT_FUNDS
    }
}

@unique
class BalanceType(Enum):
    AVAILABLE = "free"
    USED = "used"
    TOTAL = "total"
