

import datetime

from .asset import get_symbol


class PerformanceTracker():
    def __init__(self, balance, timeframe, store):
        self.timeframe = timeframe # '1m', '30m', '1h', '1d'
        self.store = store
        self.history = [balance]

    def add_period(self, start, end, balance):
        self.cash = balance.total_value
        period_pnl = self.calc_pnl(balance)
        period_returns = self.calc_returns(balance)
        self.history.append({
            'start_time': start,
            'end_time': end,
            'balance': balance,
            'pnl': period_pnl,
            'returns': period_returns
        })

    def calc_pnl(self, balance):
        prior_bal = self.periods[-1]['balance']
        return prior_bal.total_value - balance.total_value

    def calc_returns(self, balance):
        prior_bal = self.periods[-1]['balance']
        if prior_bal.total_value == 0:
            return 0.0
        pnl = self.calc_pnl(balance)
        return pnl / prior_bal.total_value

    def save(self):
        self.store.save(self.to_dict())

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





class Portfolio():
    """
    Keeps and updates the quantity and price of a position for an Asset.
    The position price represents the average price of all orders placed
    over time.
    Attributes:
      - asset (Asset): the asset held in the position
      - quantity (float): quantity in base currency (# of shares)
      - cost_price (float): average volume-weighted price of position (quote currency)

    Reference Impls:
    https://github.com/quantopian/zipline/blob/master/zipline/protocol.py#L143
    """

    def __init__(self, cash_currency, balance, positions, tracker):
        self.cash_currency = cash_currency
        self.starting_cash = balance[cash_currency]
        self.balance = balance
        self.positions = positions
        self.pnl = 0.0
        self.returns = 0.0
        self.tracker = tracker
        self.exchange_rates = exchange_rates

    def update(self, exchange_rates):
        self.exchange_rates = exchange_rates
        self.history.add_period(balance)

    @property
    def cash_balance(self):
        return self.balance[self.cash_currency]

    def total_value(self):
        return get_total_value(self.balance, self.exchange_rates)

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



def get_total_value(balance, cash_currency, exchange_rates):
    cash_value = 0.0
    for currency in balance:
        symbol = get_symbol(currency, cash_currency)
        quantity = balance[currency]
        rate = exchange_rates[symbol]
        cash_value += quantity * exchange_rate
    return cash_value
