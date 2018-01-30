import json
import datetime
from copy import copy, deepcopy

from punisher.utils.encoders import EnumEncoder
from punisher.utils.dates import Timeframe
from punisher.trading.trade import TradeSide
from punisher.portfolio.balance import Balance, BalanceType
from punisher.trading.order import OrderStatus

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

    def __init__(self, cash_currency, starting_balance, perf_tracker, positions=None):
        self.cash_currency = cash_currency
        self.starting_balance = starting_balance
        self.balance = deepcopy(starting_balance)
        self.perf = perf_tracker
        self.positions = [] if positions is None else positions

    def update(self, last_update_time, orders, latest_prices):
        self.update_positions(orders, last_update_time)
        self.update_position_prices(latest_prices)
        #self.perf.add_period(last_update_time, self.cash, self.positions)

    def update_performance(self, start, end):
        self.perf.add_period(start, end, self.cash, self.positions)

    def update_positions(self, orders, last_update_time):
        for order in orders:
            # Updating postions with new orders from previous update:
            for trade in order.get_new_trades(last_update_time):
                pos = self.get_position(order.asset)
                if pos is None:
                    pos = Position(
                            asset=order.asset,
                            quantity=trade.quantity,
                            cost_price=trade.price,
                            fee=trade.fee
                        )
                    self.positions.append(pos)
                    quantity = trade.quantity
                else:
                    if order.order_type.is_sell():
                        quantity = -trade.quantity
                    else:
                        quantity = trade.quantity
                    pos.update(quantity, trade.price, trade.fee)

                # update balance with new trade info
                self.balance.update_with_trade(trade)

            # Updating balance with any failed orders
            if order.status == OrderStatus.FAILED:
                print("portfolio failed order:")
                print(order)
                self.balance.update_with_failed_order(order)

    def update_position_prices(self, latest_prices):
        """
        Updates position's latest price variable to help keep market value
        up to date.
        :latest_prices is a map of {symbol1: latest_price, symbol2: ...}
        """
        for pos in self.positions:
            pos.latest_price = latest_prices[pos.asset.symbol]

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
        # TODO: Update to use balance
        res = {'cash':0.0}
        if self.total_value == 0.0:
            return res
        for pos in self.positions:
            res[pos.asset.id] = pos.market_value / self.total_value
        res['cash'] = self.cash / self.total_value
        return res

    @property
    def positions_value(self):
        return self.perf.get_positions_value(self.positions)

    @property
    def total_value(self):
        return self.cash + self.positions_value

    @property
    def cash(self):
        return self.balance.get(self.cash_currency)[BalanceType.TOTAL]

    @property
    def starting_cash(self):
        return self.starting_balance.get(self.cash_currency)[BalanceType.TOTAL]

    def to_dict(self):
        return {
            'cash_currency': self.cash_currency,
            'starting_balance': self.starting_balance.to_dict(),
            'balance': self.balance.to_dict(),
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
        dct = deepcopy(dct)
        port = Portfolio(
            cash_currency=dct['cash_currency'],
            starting_balance=Balance.from_dict(dct['starting_balance']),
            perf_tracker=PerformanceTracker.from_dict(dct['performance'])
        )
        positions = []
        for idx,pos in enumerate(dct['positions']):
            positions.append(Position.from_dict(pos))
        port.positions = positions
        port.balance = Balance.from_dict(
                dct.get('balance', dct['starting_balance']))
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
