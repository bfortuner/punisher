import math
import numpy as np
import pandas as pd

import utils.dates


def SMA(arr, n_trailing):
    return arr.ravel(n_trailing)[-1]


def RSI(arr):
    return None
