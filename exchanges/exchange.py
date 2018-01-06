import abc

class Exchange(metaclass=abc.ABCMeta):

    def __init__(self, exchange_cfg):
        pass

    @abc.abstractmethod
    def fetch_ohlcv(self):
        pass

    @abc.abstractmethod
    def fetch_balance(self):
        pass

    @abc.abstractmethod
    def calculate_fee(self):
        pass

    @abc.abstractmethod
    def fetch_order(self, order):
        """:order Order object"""
        pass

    @abc.abstractmethod
    def create_limit_buy_order(self):
        pass

    @abc.abstractmethod
    def create_limit_sell_order(self):
        pass

    @abc.abstractmethod
    def cancel_order(self, order):
        pass