

import datetime

from .balance import Balance
from .balance import get_total_value
from .performance import PerformanceTracker
from utils.dates import Timeframe


class Portfolio():
    """

    Attributes:
      - asset (Asset): the asset held in the position
      - quantity (float): quantity in base currency (# of shares)
      - cost_price (float): average volume-weighted price of position (quote currency)

    Reference Impls:
    https://github.com/quantopian/zipline/blob/master/zipline/protocol.py#L143
    """

    def __init__(self, starting_cash, perf_tracker, positions=None):
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.positions = [] if positions is None else positions
        self.positions_value = self.get_positions_cash_value()
        self.perf = perf_tracker

    def get_position_weights(self):
        """
        https://github.com/quantopian/zipline/blob/master/zipline/protocol.py#L177
        """
        pass

    def update(self, positions):
        # do we adjust positions based on orders here?
        start_time = datetime.datetime.utcnow()
        self.tracker.add_period(start_time, self.cash, positions)

    def total_value(self):
        return self.cash + self.positions_value

    def to_dict(self):
        return vars(self)

    @classmethod
    def from_dict(self, d):
        pass

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            cls=EnumEncoder,
            indent=4)

    @classmethod
    def from_json(self, json_str):
        dct = json.loads(json_str)
        return self.from_dict(dct)

    def __repr__(self):
        return self.to_json()



# Later (when we need to handle non-cash quoted positions)
def get_total_value(balance, cash_currency, exchange_rates):
    cash_value = 0.0
    for currency in balance.currencies:
        symbol = get_symbol(currency, cash_currency)
        quantity = balance.get(currency[TOTAL])
        rate = exchange_rates[symbol]
        cash_value += quantity * exchange_rate
    return cash_value
