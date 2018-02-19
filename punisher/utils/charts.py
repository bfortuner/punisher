import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

from . import dates


def plot_prices(time, close, fs=(12,6), title="Price"):
    fig, ax = plt.subplots()
    ax.plot(time, close)

#     years = mdates.YearLocator()   # every year
#     months = mdates.MonthLocator()  # every month
#     yearsFmt = mdates.DateFormatter('%Y')
#     monthsFmt = mdates.DateFormatter('%m')
#     ax.xaxis.set_major_locator(years)
#     ax.xaxis.set_major_formatter(yearsFmt)
#     ax.xaxis.set_minor_locator(months)
#     ax.xaxis.set_minor_formatter(monthsFmt)

    # datemin = datetime.date(r.date.min().year, 1, 1)
    # datemax = datetime.date(r.date.max().year + 1, 1, 1)
    # ax.set_xlim(datemin, datemax)

    def price(x):
        return '$%1.4f' % x
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.format_ydata = price
    ax.grid(True)

    fig.autofmt_xdate(rotation=30)
    fig.set_size_inches(fs)
    plt.title(title)
    plt.show()

def plot_range(df, start, end, column_name):
    df = dates.get_time_range(df, start, end)
    vals = df[['utc', column_name]].values
    plot_prices(vals[:,0], vals[:,1], title=column_name)
