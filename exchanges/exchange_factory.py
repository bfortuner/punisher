import config as cfg
from live_exchange import LiveExchange
from simulated_exchange import SimulatedExchange

def get_exchanges(exchange_ids):
    exchanges = []
    for id in exchange_ids:
        exchange = get_exchange(id)
        if exchange:
            print("Unable to get Exchange {}".format(id))
        else:
            exchanges.append(exchange)

def get_exchange(exchange_id):

    exchange_cfg = load_exchange_cfg(exchange_id)

    # TODO: Check if exchange exists in ccxt

    return LiveExchange(exchange_id, exchange_cfg)


def load_exchange_cfg(exchange_id):
    # TODO: figure out how we want to load configs for exchanges
    pass

