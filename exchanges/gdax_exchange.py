import config as cfg
import constants as c
from clients.gdax_client import gdax


class GDAX():
    def __init__(self, endpoint):
        self.account_id = cfg.GDAX_ACCOUNT_ID
        self.api_key = cfg.GDAX_API_KEY
        self.api_secret_key = cfg.GDAX_SECRET_KEY
        self.endpoint = endpoint

    def get_public_client(self):
        pass

    def get_private_client(self):
        pass

    def buy(self, pair, quantity, limit_price):
        pass

    def sell(self, pair, quantity, limit_price):
        pass

    def get_price(self, pair):
        pass

    def get_historical_price(self, symbol, start, end, timestep):
        pass

