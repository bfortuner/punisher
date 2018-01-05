from enum import Enum, unique


@unique
class TradeMode(Enum):
    BACKTEST = 0
    SIMULATE = 1
    LIVE = 2


class Punisher():
    def __init__(self):
        pass