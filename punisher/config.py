
import os
import logging
from os.path import join, dirname
from dotenv import load_dotenv

# Load env variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path, verbose=True)

# App
APP_NAME = os.environ.get('APP_NAME', 'PUNISHER')
APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'secret_key')
DATA_DIR = os.environ.get('DATA_DIR', '.data/')
WEIGHTS_DIR = os.environ.get('WEIGHTS_DIR', '.weights/')
TESTING = os.environ.get('TESTING', False)
DEBUG = os.environ.get('DEBUG', True)
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
APP_LOG_LEVEL = logging.INFO
MAIL_LOG_LEVEL = logging.ERROR

# AWS
AWS_REGION = 'us-west-2'
AWS_ACCOUNT_ID = 'account_id'
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID', 'password')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'password')


### Exchanges ###

# GDAX
GDAX_ACCOUNT_ID = os.environ.get('GDAX_ACCOUNT_ID')
GDAX_API_KEY = os.environ.get('GDAX_API_KEY')
GDAX_API_SECRET_KEY = os.environ.get('GDAX_API_SECRET_KEY')
GDAX_PASSPHRASE = os.environ.get('GDAX_PASSPHRASE')
GDAX_ENDPOINT = os.environ.get('GDAX_ENDPOINT')
GDAX_WEBSOCKET = os.environ.get('GDAX_WEBSOCKET')
GDAX_BTC_ACCOUNT = os.environ.get('GDAX_BTC_ACCOUNT')
GDAX_ETH_ACCOUNT = os.environ.get('GDAX_ETH_ACCOUNT')
GDAX_LTC_ACCOUNT = os.environ.get('GDAX_LTC_ACCOUNT')
GDAX_USD_ACCOUNT = os.environ.get('GDAX_USD_ACCOUNT')

# Poloniex
POLONIEX_API_KEY = os.environ.get('POLONIEX_API_KEY')
POLONIEX_API_SECRET_KEY = os.environ.get('POLONIEX_API_SECRET_KEY')

# Binance
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
BINANCE_API_SECRET_KEY = os.environ.get('BINANCE_API_SECRET_KEY')


### Data ###

# Brave New Coin
BNC_API_KEY = os.environ.get('BNC_API_KEY', 'none')
BNC_ENDPOINT = 'https://bravenewcoin-mwa-historic-v1.p.mashape.com'

# Twitter
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

# Catalyst
CATALYST_DATA_PATH = os.environ.get('CATALYST_DATA_PATH')

# DEFAULT funds
DEFAULT_FUNDS = 10000



def init_dirs():
    dirs = [DATA_DIR, WEIGHTS_DIR]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)

init_dirs()
