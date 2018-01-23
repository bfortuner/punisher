from punisher.trading import coins

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

# Metadata
OHLCV_COLUMNS = ['epoch', 'open', 'high', 'low', 'close', 'volume']

# Record
ORDERS_FNAME = 'orders.csv'
DECISIONS_FNAME = 'decisions.csv'
RECORD_DATA_FNAME = 'data.csv'
CONFIG_FNAME = 'config.json'

# Balance
DEFAULT_BALANCE = {
    coins.BTC: {'free': 1.0, 'used':0.0, 'total': 1.0},
    'free': {coins.BTC: 1.0},
    'used': {coins.BTC: 0.0},
    'total': {coins.BTC: 1.0},
    'cash_currency': coins.BTC,
    'starting_cash': 1.0,
}

# Feed
DEFAULT_30M_FEED_CSV_FILENAME = 'paper_ETH_BTC_30m.csv'

# Min Asset quantities for live exchange orders
MIN_BTC=.001
MIN_ETH=.01
MIN_BNB=1
MIN_USDT=1
