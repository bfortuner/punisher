import ccxt

import punisher.constants as c
import punisher.config as cfg

from punisher.trading import coins

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
        'verbose': False,
        'usd_coin': coins.USDT,
        'cash_coins': set([coins.BTC, coins.ETH]),
    },
    GEMINI: {
        'apiKey': cfg.GEMINI_API_KEY,
        'secret': cfg.GEMINI_API_SECRET_KEY,
        'usd_coin': coins.USD,
        'cash_coins': set([coins.BTC, coins.ETH, coins.USD]),
        'verbose':False,
    },
    GDAX: {
        'apiKey': cfg.GDAX_API_KEY,
        'secret': cfg.GDAX_API_SECRET_KEY,
        'password': cfg.GDAX_PASSPHRASE,
        'usd_coin': coins.USD,
        'cash_coins': set([coins.BTC, coins.ETH, coins.USD]),
        'verbose':False,
    },
    BINANCE: {
        'apiKey': cfg.BINANCE_API_KEY,
        'secret': cfg.BINANCE_API_SECRET_KEY,
        'usd_coin': coins.USDT,
        'cash_coins': set([coins.BTC, coins.ETH]),
        'verbose':False,
    },
    PAPER: {
        'data_provider_exchange_id': DEFAULT_EXCHANGE_ID,
        'balance': c.DEFAULT_BALANCE,
        'usd_coin': coins.USD,
        'cash_coins': set([coins.BTC, coins.ETH, coins.USD]),
        'verbose':False,
    }
}
