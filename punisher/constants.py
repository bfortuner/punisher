# Datasets
TRAIN = 'trn'
VAL = 'val'
TEST = 'tst'

# File extensions
JSON = '.json'
BCOLZ = '.bc'
CSV = '.csv'

# PyTorch
MODEL_EXT = '.mdl'
WEIGHTS_EXT = '.th'
OPTIM_EXT = '.th'

# Exchanges
GDAX = 'gdax'
COINBASE = 'coinbase'
GEMINI = 'gemini'
BINANCE = 'binance'
POLONIEX = 'poloniex'
BNC = 'bravenewcoin'
PAPER = 'paper'

# Currencies
ADA = 'ADA'
BTC = 'BTC'
ETH = 'ETH'
LTC = 'LTC'
USD = 'USD'
XRP = 'XRP'
XMR = 'XMR'
USDT = 'USDT'
DASH = 'DASH'
XEM = 'XEM'
ZEC = 'ZEC'
NXT = 'NXT'
STR = 'STR'
REP = 'REP'
BCH = 'BCH'
BTS = 'BTS'

# Pairs
BTC_USD = 'BTC-USD'
ETH_USD = 'ETH-USD'
LTC_USD = 'LTC-USD'

# Metadata
OHLCV_COLUMNS = ['epoch', 'open', 'high', 'low', 'close', 'volume']

# Record
ORDERS_FNAME = 'orders.csv'
DECISIONS_FNAME = 'decisions.csv'
RECORD_DATA_FNAME = 'data.csv'
CONFIG_FNAME = 'config.json'

# Backtest
DEFAULT_DATA_PROVIDER_EXCHANGE = BINANCE

# Balance
DEFAULT_BALANCE = {
    BTC: {'free': 1.0, 'used':0.0, 'total': 1.0},
    'free': {BTC: 1.0},
    'used': {BTC: 0.0},
    'total': {BTC: 1.0},
}

# Feed
DEFAULT_30M_FEED_CSV_FILENAME = 'paper_ETH_BTC_30m.csv'

# Min Asset quantities for live exchange orders
MIN_BTC=.001
MIN_ETH=.01
MIN_BNB=1
MIN_USDT=1
