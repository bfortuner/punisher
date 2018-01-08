

import datetime

from utils.dates import Timeframe

from trading.order import SELL_ORDER_TYPES

from .balance import Balance
from .balance import get_total_value
from .performance import PerformanceTracker
from .position import Position



class Portfolio():
    """
    Attributes:
      - starting_cash (float): Amount of cash
      - perf_tracker (PerformanceTracker): Records PnL for each period
      - positions (list): list of existing Positions

    Reference Impls:
    https://github.com/quantopian/zipline/blob/master/zipline/protocol.py#L143
    """

    def __init__(self, starting_cash, perf_tracker, positions=None):
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.perf = perf_tracker
        self.positions = [] if positions is None else positions

    def update(self, filled_orders):
        self.update_positions(filled_orders)
        start_time = datetime.datetime.utcnow()
        self.perf.add_period(start_time, self.cash, self.positions)

    def update_positions(self, filled_orders):
        for order in filled_orders:
            pos = self.get_position(order.asset)
            if pos is None:
                pos = Position(order.asset, order.quantity, order.price)
                self.positions.append(pos)
                quantity = order.quantity
            else:
                if order.order_type in SELL_ORDER_TYPES:
                    quantity = -order.quantity
                else:
                    quantity = order.quantity
                pos.update(quantity, order.price)
            self.cash -= quantity * order.price

    def get_position(self, asset):
        for pos in self.positions:
            if pos.asset.id == asset.id:
                return pos
        return None

    @property
    def weights(self):
        weights = {}
        for pos in self.positions:
            weights[pos.asset.id] = pos.market_value / self.total_value
        weights['cash'] = self.cash / self.total_value
        return weights

    @property
    def positions_value(self):
        return self.perf.get_positions_value(self.positions)

    @property
    def total_value(self):
        return self.cash + self.positions_value

    def to_dict(self):
        return {
            'starting_cash': self.starting_cash,
            'cash': self.cash,
            'weights': self.weights,
            'pnl': self.perf.pnl,
            'returns': self.perf.returns,
            'total_value': self.total_value,
            'positions': [pos.to_dict() for pos in self.positions]
        }

    def __repr__(self):
        return str(vars(self))



# Later (when we need to handle non-cash quoted positions)
def get_total_value(balance, cash_currency, exchange_rates):
    cash_value = 0.0
    for currency in balance.currencies:
        symbol = get_symbol(currency, cash_currency)
        quantity = balance.get(currency[TOTAL])
        rate = exchange_rates[symbol]
        cash_value += quantity * exchange_rate
    return cash_value
