

import datetime

from .balance import Balance
from .balance import get_total_value
from utils.dates import Timeframe


class PerformanceTracker():
    def __init__(self, starting_cash, timeframe, store=None):
        self.starting_cash = starting_cash
        self.timeframe = timeframe
        self.store = store
        self.periods = []
        self.pnl = 0.0
        self.returns = 0.0

    def add_period(self, start, cash, positions):
        if len(self.periods) == 0:
            start_cash = self.starting_cash
            start_pos_val = 0.0
        else:
            end_cash = self.periods[-1]['ending_cash']
            start_pos_val = self.periods[-1]['ending_value']
        positions_value = self.get_positions_value(positions)
        end_val = positions_value + end_cash
        start_val = start_pos_val + start_cash
        pnl = self.calc_pnl(start_val, end_val)
        returns = self.calc_returns(start_val, end_val)
        self.periods.append({
            'start_time': start,
            'end_time': start + timeframe.value['delta'],
            'starting_cash': start_cash,
            'ending_cash': end_cash,
            'starting_value': start_val
            'ending_value': end_val
            'positions': positions,
            'pnl': pnl,
            'returns': returns
        })
        self.update_performance()

    def update_performance(self):
        if len(self.periods) == 1:
            self.pnl = self.periods[0]['pnl']
            self.returns = self.periods[0]['returns']
        else:
            end_period = self.periods[-1]
            self.pnl = self.calc_pnl(
                self.starting_cash, end_period['ending_value'])
            self.returns = self.calc_returns(
                self.starting_cash, end_period['ending_value'])
        self.save()

    def calc_pnl(self, start_val, end_val):
        return end_val - start_val

    def calc_returns(self, start_val, end_val):
        if start_val == 0:
            return 0.0
        pnl = self.calc_pnl(start_val, end_val)
        return pnl / start_val

    def get_positions_value(self, positions):
        """
        TODO: Update to handle assets where the quote cash_currency
        is not the cash currency. E.g. Cash is USD but asset is ETH/BTC.

        Right now it assumes all positions are quoted in cash.
        """
        total = 0.0
        for pos in self.positions:
            total += pos.market_value
        return total

    def save(self):
        if store:
            store.save(self.periods)


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
