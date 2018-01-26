import json
from enum import Enum, unique

from punisher.trading import coins


@unique
class BalanceType(Enum):
    FREE = "free"
    USED = "used"
    TOTAL = "total"


class Balance():
    def __init__(self, cash_currency=coins.BTC, starting_cash=1.0):
        self.free = {cash_currency: starting_cash}
        self.used = {cash_currency: 0.0}
        self.total = {cash_currency: 0.0}

    @property
    def currencies(self):
        return list(self.total.keys())

    def get(self, currency):
        if currency not in self.currencies:
            self.add_currency(currency)
        return {
            BalanceType.FREE: self.free[currency],
            BalanceType.USED: self.used[currency],
            BalanceType.TOTAL: self.total[currency],
        }

    def update_with_created_orders(self, orders):
        for order in orders:
            self.update_with_created_order(order)

    def update_with_created_order(self, order):
        """
        Helper method to update with a newly created order
        """
        order_type = order.order_type
        asset = order.asset
        price = order.price
        quantity = order.quantity
        self._ensure_asset_in_balance(asset)
        if order_type.is_buy():
            # Moving quote funds into Used from free as we are trying to buy
            # with it
            self.update(
                currency=asset.quote,
                delta_free=-(price * quantity),
                delta_used=(price * quantity)
            )

        elif order_type.is_sell():
            # Moving some of our base into Used as we are trying to sell it
            self.update(
                currency=asset.base,
                delta_free=0.0,
                delta_used=-quantity
            )

    def update_with_failed_orders(self, orders):
        for order in orders:
            self.update_with_failed_order(order)

    def update_with_failed_order(self, order):
        """
        Helper method to update with a recently cancelled order
        ASSUMES order does NOT have new trades
        """
        order_type = order.order_type
        asset = order.asset
        price = order.price
        quantity = order.quantity
        if order_type.is_buy():
            # Removing the remaining quote funds used for the offer now that we are
            # no longer trying to purchase any additional base
            trade_cost = sum(
            [(trade.price * trade.quantity) for trade in order.trades])
            quote_not_used = (price * quantity) - trade_cost
            self.update(
                currency=asset.quote,
                delta_free=quote_not_used,
                delta_used=-quote_not_used,
            )

        elif order_type.is_sell():
            # Adding remaining quantity back to free as it's no longer for sale
            base_sold = sum([trade.quantity for trade in order.trades])
            base_unsold = quantity - base_sold
            self.update(
                currency=asset.base,
                delta_free=base_unsold,
                delta_used=-base_unsold
            )

    def update_with_trades(self, trades):
        for trade in trades:
            self.update_with_trade(trade)

    def update_with_trade(self, trade):
        side = trade.side
        asset = trade.asset
        price = trade.price
        quantity = trade.quantity
        fee = trade.fee

        if side.is_buy():
            # Performing the buy... so we take the funds allocated for trading
            # and subtract them by the trade cost
            # we then increase our base funds by the quantity of the trade
            self.update(
                currency=asset.quote,
                delta_free=0.0,
                delta_used=-((price * quantity) + fee)
            )
            self.update(
                currency=asset.base,
                delta_free=quantity,
                delta_used=0.0
            )

        elif side.is_sell():
            # Performing the sell.... so we add funds to quote based on the
            # sale cost
            # We then remove trade quantity from the allocated base quantity
            # being used for trading
            self.update(
                currency=asset.quote,
                delta_free=((price * quantity) - fee),
                delta_used=0.0
            )
            self.update(
                currency=asset.base,
                delta_free=0.0,
                delta_used=-quantity
            )

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


## Helpers

def get_total_value(balance, cash_currency, exchange_rates):
    cash_value = 0.0
    for currency in balance.currencies:
        symbol = coins.get_symbol(currency, cash_currency)
        quantity = balance.get(currency)[BalanceType.TOTAL]
        rate = exchange_rates[symbol]
        cash_value += quantity * exchange_rate
    return cash_value
