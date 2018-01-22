import json
from enum import Enum, unique

from punisher.trading import coins

from .asset import get_symbol


class Balance():
    def __init__(self, cash_currency=coins.BTC, starting_cash=1.0):
        self.free = {cash_currency: starting_cash}
        self.used = {cash_currency: 0.0}
        self.total = {cash_currency: 0.0}

    @property
    def currencies(self):
        return list(self.total.keys())

    def get(self, currency):
        return {
            BalanceType.FREE: self.free[currency],
            BalanceType.USED: self.used[currency],
            BalanceType.TOTAL: self.total[currency],
        }

    def update_by_order(self, asset, quantity, price, order_type):
        self._ensure_asset_in_balance(asset)
        if order_type.is_buy():
            self.update(
                currency=asset.quote,
                delta_free=-(price * quantity),
                delta_used=0.0)
            self.update(
                currency=asset.base,
                delta_free=quantity,
                delta_used=0.0)

        elif order_type.is_sell():
            self.update(
                currency=asset.quote,
                delta_free=(price * quantity),
                delta_used=0.0)
            self.update(
                currency=asset.base,
                delta_free=-quantity,
                delta_used=0.0)

    def update(self, currency, delta_free, delta_used):
        self.free[currency] += delta_free
        self.used[currency] += delta_used
        self.total[currency] = self.free[currency] + self.used[currency]

    def add_currency(self, currency):
        assert currency not in self.currencies
        self.free[currency] = 0.0
        self.used[currency] = 0.0
        self.total[currency] = 0.0

    def is_balance_sufficient(self, asset, quantity, price, order_type):
        """
        We don't support Margin orders yet.
        All balances must be positive.
        """
        self._ensure_asset_in_balance(asset)
        if order_type.is_buy():
            return price * quantity <= self.get(
                asset.quote)[BalanceType.FREE]
        elif order_type.is_sell():
            return quantity <= self.get(
                asset.base)[BalanceType.FREE]
        raise Exception("Order type {} not supported".format(order_type))

    def _ensure_asset_in_balance(self, asset):
        if asset.base not in self.currencies:
            self.add_currency(asset.base)
        if asset.quote not in self.currencies:
            self.add_currency(asset.quote)

    def to_dict(self):
        dct = {}
        for curr in self.currencies:
            dct[curr] = {
                BalanceType.FREE.value : self.free[curr],
                BalanceType.USED.value : self.used[curr],
                BalanceType.TOTAL.value : self.total[curr],
            }
        dct[BalanceType.FREE.value] = self.free
        dct[BalanceType.USED.value] = self.used
        dct[BalanceType.TOTAL.value] = self.total
        return dct

    @classmethod
    def from_dict(self, dct):
        bal = Balance(
            cash_currency=coins.BTC,
            starting_cash=0.0
        )
        bal.free = dct[BalanceType.FREE.value]
        bal.used = dct[BalanceType.USED.value]
        bal.total = dct[BalanceType.TOTAL.value]
        return bal

    def to_json(self):
        dct = self.to_dict()
        return json.dumps(dct, indent=4)

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        return self.to_json()


@unique
class BalanceType(Enum):
    FREE = "free"
    USED = "used"
    TOTAL = "total"



## Helpers

def get_total_value(balance, cash_currency, exchange_rates):
    cash_value = 0.0
    for currency in balance.currencies:
        symbol = get_symbol(currency, cash_currency)
        quantity = balance.get(currency)[BalanceType.TOTAL]
        rate = exchange_rates[symbol]
        cash_value += quantity * exchange_rate
    return cash_value
