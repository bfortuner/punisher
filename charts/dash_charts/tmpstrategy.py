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
from utils.dates import Timeframe


from charts.dash_viz import generate_table
from charts.dash_viz import DashViz, DashDataProvider


# https://plot.ly/dash/live-updates
# https://medium.com/@LeonFedden/deep-cryptocurrency-trading-1e64af6d280a
# https://plot.ly/dash/urls

CHART_REFRESH_SEC = 5
DATA_REFRESH_SEC = 30

class StrategyDataProvider(DashDataProvider):

    def __init__(self, record, refresh_sec=30):
        super().__init__(refresh_sec)
        self.record = record
        self.ohlcv = {}

    def initialize(self):
        super().initialize()

    def update(self):
        pass

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



def change_plot(value, n):
    dropdown_val = value
    return 'Market Prices ' + str(value)

def plot_olhc(data, value, n):
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

def plot_v(data, value, n):
    ohlcv = data.get_all()
    return {
        'data': [go.Bar(x=ohlcv['time_utc'],
                        y=ohlcv['volume'])],
        'layout': dict(title="Volume")
    }


if __name__ == "__main__":
    asset = Asset(c.ETH, c.BTC)
    exchange = load_exchange(c.BINANCE)
    timeframe = Timeframe.ONE_MIN
    feed_fpath = get_price_data_fpath(asset, exchange.id,
        period=timeframe)
    feed = ExchangeDataFeed(
        exchange=exchange, assets=[asset],
        timeframe=timeframe, fpath=feed_fpath,
        start=datetime.datetime.utcnow()-datetime.timedelta(hours=1))
    data = StrategyDataProvider(feed, DATA_REFRESH_SEC)

    dropdown_val = asset.symbol
    layout = html.Div([
        html.Div([
            html.H1('Punisher', id='h1_title'),
            # dcc.Dropdown(
            #     id='symbol-dropdown',
            #     options=[{'label': key, 'value': key}
            #              for key in data.get_symbols()],
            #     value=dropdown_val
            # ),
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
                ], className="eight columns"),
                html.Div([
                    dcc.Graph(
                        id='market-prices-hist',
                        config={
                            'displayModeBar': False
                        }
                    ),
                ], className="four columns")
            ], className="row"),
            dcc.Interval(
                id='interval-component',
                interval=CHART_REFRESH_SEC*1000,
                n_intervals=0
            )
        ], className="row")
    ])

    app = dash.Dash()
    app.layout = layout
    app.css.append_css({
        "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
    })
    app.callback(
        Output('v', 'figure'),
        [Input(data),
        Input('symbol-dropdown', 'value'),
        Input('interval-component', 'n_intervals')]
     )(plot_v)

    app.callback(
        Output('ohlc', 'figure'),
        [Input(data),
        Input('symbol-dropdown', 'value'),
        Input('interval-component', 'n_intervals')]
     )(plot_olhc)

     # @app.callback(Output('h1_title', 'title'),
     #               [Input('symbol-dropdown', 'value'),
     #                Input('interval-component', 'n_intervals')])
    # app.callback(
    #     Output('v', 'figure'),
    #     [Input('symbol-dropdown', 'value'),
    #     Input('interval-component', 'n_intervals')])
    # app.callback(
    #     Output('ohlc', 'figure'),
    #     [Input('symbol-dropdown', 'value'),
    #     Input('interval-component', 'n_intervals')])

    viz = DashViz(app)
    viz.run()
