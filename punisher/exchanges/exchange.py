import abc


class Exchange(metaclass=abc.ABCMeta):
    def __init__(self, ex_id):
        self.id = ex_id

    @abc.abstractmethod
    def create_limit_buy_order(self, asset, quantity, price):
        pass

    @abc.abstractmethod
    def create_limit_sell_order(self, asset, quantity, price):
        pass

    @abc.abstractmethod
    def create_market_buy_order(self, asset, quantity):
        pass

    @abc.abstractmethod
    def create_market_sell_order(self, asset, quantity):
        pass

    @abc.abstractmethod
    def cancel_order(self, order_id):
        pass

    @abc.abstractmethod
    def deposit(self, asset):
        pass

    @abc.abstractmethod
    def withdraw(self, symbol, quantity, address, params=None):
        pass

    @staticmethod
    def get_bid_ask_spread(order_book):
        bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        return { 'bid': bid, 'ask': ask, 'spread': spread }

    @abc.abstractmethod
    def calculate_fee(self):
        pass

    @abc.abstractmethod
    def cash_coins(self):
        pass

    @abc.abstractmethod
    def usd_coin(self):
        pass

    def is_balance_sufficient(self, asset, quantity, price, order_type):
        return self.fetch_balance().is_balance_sufficient(
            asset, quantity, price, order_type)

    def get_default_params_if_none(self, params):
        return {} if params is None else params
