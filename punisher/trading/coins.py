# Coins
ADA = 'ADA'
BCH = 'BCH'
BTS = 'BTS'
DASH = 'DASH'
LTC = 'LTC'
NXT = 'NXT'
REP = 'REP'
STR = 'STR'
XEM = 'XEM'
XMR = 'XMR'
XRP = 'XRP'
ZEC = 'ZEC'

# Cash Coins
BTC = 'BTC'
ETH = 'ETH'
USD = 'USD'
USDT = 'USDT'


COINS = set([
    ADA, BCH, BTC, BTS, DASH, ETH,
    LTC, NXT, REP, STR, USD, USDT,
    XEM, XMR, XRP, ZEC
])

CASH_COINS = set([
    BTC, ETH, USD, USDT
])

class CoinNotSupportedException(Exception):
    def __init__(self, coin):
        super().__init__("Coin {:s} not among supported coins: {}".format(
            coin, COINS))

class CashNotSupportedException(Exception):
    def __init__(self, coin):
        super().__init__("Coin {:s} not among supported cash coins: {}".format(
            coin, CASH_COINS))

def is_usd(coin):
    return coin in [USD, USDT]

def is_cash(coin):
    return coin in CASH_COINS

def get_id(base, quote):
    return base + '_' + quote

def get_symbol(base, quote):
    return base + '/' + quote
