from exchange import Exchange

class SimulatedExchange(Exchange):

    def fetch_ohlcv(self):
        pass

    def fetch_balance(self):
        pass

    def calculate_fee(self):
        pass

    def fetch_order(self, order):
        pass

    def create_limit_buy_order(self):
        pass

    def create_limit_sell_order(self):
        pass

    def cancel_order(self, order):
        pass