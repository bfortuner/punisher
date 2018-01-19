import os
import sys
import math
import time
import datetime
import random
from glob import glob
from pprint import pprint
import operator
import copy
import traceback
import requests
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import dash

# Machine learning
# import torch
# import torchvision
# import torch.nn as nn
# import torch.nn.init as init
# import torch.optim as optim
# import torch.nn.functional as F
# from torch.autograd import Variable
# import torch.autograd as autograd
# import torchvision.models

# Clients
import ccxt

# Config
import punisher.config as cfg
import punisher.constants as c

# Data
from punisher.data import ohlcv
from punisher.data.feed import CSVDataFeed, ExchangeDataFeed
from punisher.data.feed import EXCHANGE_FEED, CSV_FEED
from punisher.data.store import FileStore
from punisher.data.store import DATA_STORES, FILE_STORE

# Utils
import punisher.utils.dates
from punisher.utils.dates import Timeframe
import punisher.utils.charts
import punisher.utils.general
import punisher.utils.encoders

# Trading
from punisher.trading.context import Context
from punisher.trading.runner import TradeMode
from punisher.trading.context import get_default_backtest_config
from punisher.trading.order import Order
from punisher.trading.order import OrderStatus, OrderType
from punisher.trading import order_manager
from punisher.trading.record import Record
from punisher.trading import runner
import punisher.trading.coins

# Exchanges
from punisher.exchanges.exchange import load_exchange
from punisher.exchanges.exchange import CCXTExchange
from punisher.exchanges.exchange import PaperExchange
from punisher.exchanges.exchange import load_feed_based_paper_exchange
from punisher.exchanges.exchange import load_ccxt_based_paper_exchange
from punisher.exchanges.data_providers import FeedExchangeDataProvider
from punisher.exchanges.data_providers import CCXTExchangeDataProvider

# Portfolio
from punisher.portfolio.asset import Asset
from punisher.portfolio.position import Position
from punisher.portfolio.balance import Balance, BalanceType
from punisher.portfolio.portfolio import Portfolio
from punisher.portfolio.performance import PerformanceTracker

# Strategies
from punisher.strategies.simple import SimpleStrategy

# Visualizations
from punisher.charts.data_providers import RecordChartDataProvider
