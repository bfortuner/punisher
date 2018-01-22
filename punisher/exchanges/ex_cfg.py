import ccxt

import punisher.constants as c
import punisher.config as cfg

GDAX = 'gdax'
GEMINI = 'gemini'
BINANCE = 'binance'
POLONIEX = 'poloniex'
BNC = 'bravenewcoin'
PAPER = 'paper'

DEFAULT_EXCHANGE_ID = BINANCE

EXCHANGE_CLIENTS = {
    BINANCE: ccxt.binance,
    GDAX: ccxt.gdax,
    GEMINI: ccxt.gemini,
    POLONIEX: ccxt.poloniex
}

EXCHANGE_CONFIGS = {
    POLONIEX: {
        'apiKey': cfg.POLONIEX_API_KEY,
        'secret': cfg.POLONIEX_API_SECRET_KEY,
    },
    GDAX: {
        'apiKey': cfg.GDAX_API_KEY,
        'secret': cfg.GDAX_API_SECRET_KEY,
        'password': cfg.GDAX_PASSPHRASE,
        'verbose':False,
    },
    BINANCE: {
        'apiKey': cfg.BINANCE_API_KEY,
        'secret': cfg.BINANCE_API_SECRET_KEY,
        'verbose':False,
    },
    PAPER: {
        'data_provider_exchange_id': DEFAULT_EXCHANGE_ID,
        'balance': c.DEFAULT_BALANCE
    }
}
