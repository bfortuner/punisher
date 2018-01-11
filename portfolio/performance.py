import json
import datetime
import copy

import pandas as pd

from utils.encoders import EnumEncoder
from utils.dates import Timeframe
from utils.dates import date_to_str, str_to_date

from .balance import Balance
from .balance import get_total_value


class PerformanceTracker():
    def __init__(self, starting_cash, timeframe, store=None):
        self.starting_cash = starting_cash
        self.timeframe = timeframe
        self.store = store
        self.periods = []
        self.pnl = 0.0
        self.returns = 0.0

    def add_period(self, start, cash, positions):
        positions_value = self.get_positions_value(positions)
        if len(self.periods) == 0:
            start_cash = self.starting_cash
            start_val = self.starting_cash
        else:
            start_cash = self.periods[-1]['end_cash']
            start_val = self.periods[-1]['end_value']
        end_val = positions_value + cash
        pnl = self.calc_pnl(self.starting_cash, end_val)
        returns = self.calc_returns(self.starting_cash, end_val)
        self.periods.append({
            'start_time': start,
            'end_time': start + self.timeframe.value['delta'],
            'start_cash': start_cash,
            'end_cash': cash,
            'start_value': start_val,
            'end_value': end_val,
            'pnl': pnl,
            #'positions': self.make_positions_dict(positions),
            'returns': returns,
        })
        self.update_performance()

    def update_performance(self):
        if len(self.periods) > 0:
            self.pnl = self.periods[-1]['pnl']
            self.returns = self.periods[-1]['returns']

    def calc_pnl(self, start_val, end_val):
        return end_val - start_val

    def calc_returns(self, start_val, end_val):
        if start_val == 0.0:
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
        for pos in positions:
            total += pos.market_value
        return total

    def make_positions_dict(self, positions):
        return [pos.to_dict() for pos in positions]

    def to_dict(self):
        dct = copy.deepcopy(vars(self))
        dct['timeframe'] = self.timeframe.name
        dct.pop('store')
        for p in dct['periods']:
            p['start_time'] = date_to_str(p['start_time'])
            p['end_time'] = date_to_str(p['end_time'])
        return dct

    @classmethod
    def from_dict(self, dct):
        dct = copy.deepcopy(dct)
        perf = PerformanceTracker(
            starting_cash=dct['starting_cash'],
            timeframe=Timeframe[dct['timeframe']],
        )
        for p in dct['periods']:
            p['start_time'] = str_to_date(p['start_time'])
            p['end_time'] = str_to_date(p['end_time'])
        perf.periods = dct['periods']
        perf.pnl = dct['pnl']
        perf.returns = dct['returns']
        return perf

    def to_dataframe(self):
        dct = self.to_dict()
        df = pd.DataFrame(dct['periods'])
        df.set_index('start_time', inplace=True)
        return df

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            cls=EnumEncoder,
            indent=4)

    def __repr__(self):
        return self.to_json()
