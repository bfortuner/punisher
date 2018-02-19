import os
import sys
import math
import time
import datetime
import random
import pathlib
from glob import glob
from pprint import pprint
from pathlib import Path
from copy import deepcopy
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

# Config
import punisher.config as cfg
import punisher.constants as c

# Clients
import ccxt
from punisher.clients import reddit_client
from punisher.clients import twitter_client

# Data
from punisher.data.store import FileStore
from punisher.data.store import DATA_STORES, FILE_STORE

# Exchanges
from punisher.exchanges import ex_cfg
from punisher.exchanges import load_exchange
from punisher.exchanges import CCXTExchange
from punisher.exchanges import PaperExchange
from punisher.exchanges import load_feed_based_paper_exchange
from punisher.exchanges import load_ccxt_based_paper_exchange
from punisher.exchanges import FeedExchangeDataProvider
from punisher.exchanges import CCXTExchangeDataProvider

# Feeds
from punisher.feeds import ohlcv_feed
from punisher.feeds import OHLCVFileFeed
from punisher.feeds import OHLCVExchangeFeed
from punisher.feeds.ohlcv_feed import EXCHANGE_FEED, CSV_FEED

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
from punisher.trading import coins


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
