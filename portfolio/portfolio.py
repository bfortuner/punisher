


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

    def __init__(self, cash_currency, balance, positions):
        self.cash_currency = cash_currency
        self.starting_cash = balance[cash_currency]
        self.balance = balance
        self.positions = positions
        self.PnL = 0.0
        self.returns = 0.0

    @property
    def cash_balance(self):
        return self.balance[self.cash_currency]

    def total_value(self, exchange_rates):
        cash_value = 0.0
        for pos in self.positions:
            price = get_latest_price(
                self.pos.asset.quote,
                self.cash_currency,
                exchange_rates
            )
            cash_value += pos.cash_value(price)
        return cash_value

    def to_dict(self):
        return vars(self)

    def __repr__(self):
        return str(self.to_dict())
