import config as cfg
import ccxt
from live_exchange import LiveExchange
from simulated_exchange import SimulatedExchange

class ExchangeFactory():

    def __init__(self, simulated=True):
        pass

    def get_exchanges(self, exchange_ids):
        exchanges = []
        for id in exchange_ids:
            exchange = get_exchange(id)
            if exchange:
                print("Unable to get Exchange {}".format(id))
            else:
                exchanges.append(exchange)

    def get_exchange(self, exchange_id):

        exchange_cfg = self._load_exchange_cfg(exchange_id)

        # TODO: Check if exchange exists in ccxt

        if simulated:
            return SimulatedExchange(exchange_id, exchange_cfg)

        return LiveExchange(exchange_id, exchange_cfg)


    def _load_exchange_cfg(self, exchange_id):
        # TODO: figure out how we want to load configs for exchanges
        pass

