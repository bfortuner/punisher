
import math

class Position():
    """
    Keeps and updates the quantity and price of a position for an Asset.
    The position price represents the average price of all orders placed
    over time.
    Attributes:
      - asset (Asset): the asset held in the position
      - quantity (float): quantity in base currency (# of shares)
      - cost_price (float): average volume-weighted price of position (quote currency)
    """

    def __init__(self, asset, quantity, cost_price):
        self.asset = asset
        self.quantity = quantity
        self.cost_price = cost_price
        self.latest_price = cost_price

    def update(self, txn_quantity, txn_price):
        """
        txn_quantity: # of shares of transaction
            positive = buy
            negative = sell
        txn_price: price of transaction

        Cost calculated with Average Cost Basis method
        https://www.investopedia.com/terms/a/averagecostbasismethod.asp

        Reference Impls:
        https://github.com/mementum/backtrader/blob/master/backtrader/position.py
        https://github.com/quantopian/zipline/blob/master/zipline/finance/performance/position.py
        """
        total_quantity = self.quantity + txn_quantity

        if total_quantity == 0.0:
            self.cost_price = 0.0
        else:
            prev_direction = math.copysign(1, self.quantity)
            txn_direction = math.copysign(1, txn_quantity)

            if prev_direction != txn_direction:
                # we're covering a short or closing a position
                if abs(txn_quantity) > abs(self.quantity):
                    # we've closed the position and gone short
                    # or covered the short and gone long
                    self.cost_price = txn_price
            else:
                txn_value = txn_quantity * txn_price
                total_value = self.cost_value + txn_value
                self.cost_price = total_value / total_quantity

        self.quantity = total_quantity
        self.latest_price = txn_price

    @property
    def cost_value(self):
        return self.quantity * self.cost_price

    @property
    def market_value(self):
        return self.quantity * self.latest_price

    def to_dict(self):
        return {
            'asset': self.asset.to_dict(),
            'quantity': self.quantity,
            'cost_price': self.cost_price,
            'latest_price': self.latest_price
        }
