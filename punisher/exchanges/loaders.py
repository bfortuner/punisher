from copy import deepcopy

from punisher.portfolio.balance import Balance

from .ex_cfg import *
from .ccxt_exchange import CCXTExchange
from .data_providers import CCXTExchangeDataProvider
from .data_providers import FeedExchangeDataProvider
from .paper_exchange import PaperExchange


def load_exchange(ex_id, config=None):
    if ex_id not in EXCHANGE_CONFIGS.keys():
        raise NotImplemented

    if config is None:
        config = deepcopy(EXCHANGE_CONFIGS.get(ex_id))

    if ex_id == PAPER:
        dp_exchange_id = config['data_provider_exchange_id']
        balance = Balance.from_dict(config['balance'])
        return load_ccxt_based_paper_exchange(balance, dp_exchange_id)

    return CCXTExchange(ex_id, config)

def load_feed_based_paper_exchange(balance, feed, feed_ex_id):
    balance = deepcopy(balance)
    data_provider = FeedExchangeDataProvider(feed, feed_ex_id)
    return PaperExchange(feed_ex_id, balance, data_provider)

def load_ccxt_based_paper_exchange(balance, exchange_id):
    balance = deepcopy(balance)
    exchange = load_exchange(exchange_id)
    data_provider = CCXTExchangeDataProvider(exchange)
    return PaperExchange(exchange_id, balance, data_provider)
