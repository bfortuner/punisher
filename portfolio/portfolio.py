import json
import datetime
import copy

from utils.encoders import EnumEncoder
from utils.dates import Timeframe

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
                if order.order_type.is_sell():
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
    def symbols(self):
        symbols = set()
        for pos in self.positions:
            symbols.add(pos.asset.symbol)
        return list(symbols)

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
            'performance': self.perf.to_dict(),
            'positions': [pos.to_dict() for pos in self.positions]
        }

    @classmethod
    def from_dict(self, dct):
        dct = copy.deepcopy(dct)
        port = Portfolio(
            starting_cash=dct['starting_cash'],
            perf_tracker=PerformanceTracker.from_dict(dct['performance'])
        )
        positions = []
        for idx,pos in enumerate(dct['positions']):
            positions.append(Position.from_dict(pos))
        port.positions = positions
        port.cash = dct['cash']
        port.pnl = dct['pnl']
        port.returns = dct['returns']
        return port

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            cls=EnumEncoder,
            indent=4)

    def __repr__(self):
        return self.to_json()
