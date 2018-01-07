import math
import numpy as np
import pandas as pd

import utils.dates

"""
# Backtrader examples

bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
bt.indicators.WeightedMovingAverage(self.datas[0], period=25).subplot = True
bt.indicators.StochasticSlow(self.datas[0])
bt.indicators.MACDHisto(self.datas[0])
rsi = bt.indicators.RSI(self.datas[0])
bt.indicators.SmoothedMovingAverage(rsi, period=10)
bt.indicators.ATR(self.datas[0]).plot = False
"""

def SMA(arr, n_trailing):
    return arr.ravel(n_trailing)[-1]


def RSI(arr):
    return None
