import time
import datetime
from collections import deque
import threading

import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event

import config as cfg
import constants as c
from portfolio.asset import Asset
from data.ohlcv import get_price_data_fpath
from data.feed import CSVDataFeed, ExchangeDataFeed
from exchanges.exchange import load_exchange
from charts.dash_viz import generate_table
from utils.dates import Timeframe

# https://plot.ly/dash/live-updates
# https://medium.com/@LeonFedden/deep-cryptocurrency-trading-1e64af6d280a
# https://plot.ly/dash/urls

REFRESH_SEC = 5

class OHLCVProvider(object):

    def __init__(self, feed):
        self.feed = feed
        self.delay_seconds = 30
        self.ohlcv = {}
        self.thread = threading.Thread(target=self._update)
        self.thread.daemon = True
        self.thread.start()

    def initialize(self):
        self.feed.initialize()
        # Optionally include some history
        # self.ohlcv = self.feed.history(t_minus=100)

    def get_symbols(self):
        return ['ETH/BTC','LTC/BTC']

    def get_next(self):
        """
        Returns dictionary:
            {'close': 0.077,
             'high': 0.0773,
             'low': 0.0771,
             'open': 0.0772,
             'time_utc': Timestamp('2018-01-08 22:22:00'),
             'volume': 222.514}
        """
        return self.feed.next().to_dict()

    def get_all(self):
        """Returns Dataframe"""
        return self.feed.history()

    def _update(self):
        while True:
            self.feed.update()
            time.sleep(self.delay_seconds)


# asset = Asset(c.ETH, c.BTC)
# feed_fpath = get_price_data_fpath(asset, c.BINANCE, period='1m')
# feed = CSVDataFeed(feed_fpath)
# data = OHLCVProvider(feed)

asset = Asset(c.ETH, c.BTC)
exchange = load_exchange(c.BINANCE)
timeframe = Timeframe.ONE_MIN
print(exchange.timeframes)
feed_fpath = get_price_data_fpath(asset, exchange.id,
    period=timeframe)
feed = ExchangeDataFeed(
    exchange=exchange, assets=[asset],
    timeframe=timeframe, fpath=feed_fpath,
    start=datetime.datetime.utcnow()-datetime.timedelta(hours=1))
data = OHLCVProvider(feed)

selected_dropdown_value = asset.symbol

app = dash.Dash()

app.layout = html.Div([
    html.Div([
        html.H1('Punisher', id='h1_title'),
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[{'label': key, 'value': key}
                     for key in data.get_symbols()],
            value=selected_dropdown_value
        ),
        html.Div([
            dcc.Graph(
                id='ohlc',
                config={
                    'displayModeBar': False
                }
            ),
        ], className="row"),
        html.Div([
            dcc.Graph(
                id='v',
                config={
                    'displayModeBar': False
                }
            ),
        ], className="row"),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='market-prices-graph',
                    config={
                        'displayModeBar': False
                    }
                ),
                # dcc.Graph(
                #     id='spread-graph',
                #     config={
                #         'displayModeBar': False
                #     }
                # ),
            ], className="eight columns"),
            html.Div([
                dcc.Graph(
                    id='market-prices-hist',
                    config={
                        'displayModeBar': False
                    }
                ),
                # dcc.Graph(
                #     id='spread-hist',
                #     config={
                #         'displayModeBar': False
                #     }
                # ),
            ], className="four columns")
        ], className="row"),
        dcc.Interval(
            id='interval-component',
            interval=REFRESH_SEC*1000,
            n_intervals=0
        )
    ], className="row")
])
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


@app.callback(Output('h1_title', 'title'),
              [Input('symbol-dropdown', 'value'),
               Input('interval-component', 'n_intervals')])
def change_plot(value, n):
    global selected_dropdown_value
    selected_dropdown_value = value
    return 'Market Prices ' + str(value)


@app.callback(Output('ohlc', 'figure'),
              [Input('symbol-dropdown', 'value'),
               Input('interval-component', 'n_intervals')])
def plot_olhc(value, n):
    global data
    ohlcv = data.get_all()
    return {
        'data': [go.Ohlc(x=ohlcv['time_utc'],
                         open=ohlcv['open'],
                         high=ohlcv['high'],
                         low=ohlcv['low'],
                         close=ohlcv['close'],
                         showlegend=False)],
        'layout': dict(title="OHLC")
    }


@app.callback(Output('v', 'figure'),
              [Input('symbol-dropdown', 'value'),
               Input('interval-component', 'n_intervals')])
def plot_v(value, n):
    global data
    ohlcv = data.get_all()
    return {
        'data': [go.Bar(x=ohlcv['time_utc'],
                        y=ohlcv['volume'])],
        'layout': dict(title="Volume")
    }


# @app.callback(Output('market-prices-graph', 'figure'),
#               events=[Event('graph-speed-update', 'interval')])
def update_market_prices():
    global selected_dropdown_value
    global data
    prices = data.get_prices(selected_dropdown_value)
    prices = [list(p) for p in zip(*prices)]
    if len(prices) > 0:
        traces = []
        x = list(prices[3])
        for i, key in enumerate(['bid', 'ask']):
            trace = go.Scatter(x=x,
                               y=prices[i],
                               name=key,
                               opacity=0.8)
            traces.append(trace)
        return {
            'data': traces,
            'layout': dict(title="Market Prices")
        }


# @app.callback(Output('market-prices-hist', 'figure'),
#               events=[Event('graph-speed-update', 'interval')])
def update_market_prices_hist():
    global selected_dropdown_value
    global data
    prices = data.get_prices(selected_dropdown_value)
    prices = [list(p) for p in zip(*prices)]
    if len(prices) > 0:
        traces = []
        for i, key in enumerate(['bid', 'ask']):
            trace = go.Histogram(x=prices[i][-200:],
                                 name=key,
                                 opacity=0.8)
            traces.append(trace)
        return {
            'data': traces,
            'layout': dict(title="Market Prices Histogram (200 Most Recent)")
        }


# @app.callback(Output('spread-graph', 'figure'),
#               events=[Event('graph-speed-update', 'interval')])
def update_spread():
    global selected_dropdown_value
    global data
    prices = data.get_prices(selected_dropdown_value)
    prices = [list(p) for p in zip(*prices)]
    if len(prices) > 0:
        traces = []
        trace = go.Scatter(x=list(prices[3]),
                           y=list(prices[2]),
                           name='spread',
                           line=dict(color='rgb(114, 186, 59)'),
                           fill='tozeroy',
                           fillcolor='rgba(114, 186, 59, 0.5)',
                           mode='none')
        traces.append(trace)

        return {
            'data': traces,
            'layout': dict(title="Spread")
        }


# @app.callback(Output('spread-hist', 'figure'),
#               events=[Event('graph-speed-update', 'interval')])
def update_spread_hist():
    global selected_dropdown_value
    global data
    prices = data.get_prices(selected_dropdown_value)
    prices = [list(p) for p in zip(*prices)]
    if len(prices) > 0:
        traces = []
        trace = go.Histogram(x=list(prices[2][-200:]),
                             name='spread',
                             marker=dict(color='rgba(114, 186, 59, 0.5)'))
        traces.append(trace)

        return {
            'data': traces,
            'layout': dict(title="Spread Histogram (200 Most Recent)")
        }



app.run_server(port=8000, debug=True, host='0.0.0.0')
