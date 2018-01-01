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
DATA_DIR = os.environ.get('DATA_DIR', 'data/')
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
GDAX_ACCOUNT_ID = os.environ.get('GDAX_ACCOUNT_ID', 'none')
GDAX_API_KEY = os.environ.get('GDAX_API_KEY', 'none')
GDAX_API_SECRET_KEY = os.environ.get('GDAX_API_SECRET_KEY', 'none')
GDAX_PASSPHRASE = os.environ.get('GDAX_PASSPHRASE', 'none')
GDAX_ENDPOINT = os.environ.get('GDAX_ENDPOINT', 'none')
GDAX_WEBSOCKET = os.environ.get('GDAX_WEBSOCKET', 'none')
GDAX_BTC_ACCOUNT = os.environ.get('GDAX_BTC_ACCOUNT', 'none')
GDAX_ETH_ACCOUNT = os.environ.get('GDAX_ETH_ACCOUNT', 'none')
GDAX_LTC_ACCOUNT = os.environ.get('GDAX_LTC_ACCOUNT', 'none')
GDAX_USD_ACCOUNT = os.environ.get('GDAX_USD_ACCOUNT', 'none')


### Data ###

# Brave New Coin
BNC_API_KEY = os.environ.get('BNC_API_KEY', 'none')
BNC_ENDPOINT = 'https://bravenewcoin-mwa-historic-v1.p.mashape.com'

# Twitter
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY', 'none')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET', 'none')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN', 'none')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', 'none')