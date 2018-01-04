import pandas as pd
import config as cfg
perf = pd.read_pickle(cfg.CATALYST_DATA_PATH + 'data/live_algos/portfolio_optimization/daily_perf/2018-01-04.p') # read in perf DataFrame
print(dir(perf))
print(perf.viewitems())