import os
import sys
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
import dash_table_experiments as dt

import config as cfg
import constants as c
from portfolio.asset import Asset
from data.ohlcv import get_price_data_fpath
from data.feed import CSVDataFeed, ExchangeDataFeed
from trading.record import Record

from charts.dash_viz import generate_table
from utils.dates import Timeframe

EXPERIMENT_NAME = sys.argv[1]
EXPERIMENT_PATH = os.path.join(cfg.DATA_DIR, EXPERIMENT_NAME)
print("Experiment: ", EXPERIMENT_NAME)
print("RootDir: ", EXPERIMENT_PATH)
REFRESH_SEC = 5

class RecordDataProvider():
    def __init__(self, root_dir, refresh_sec=5, t_minus=30):
        self.root_dir = root_dir
        self.refresh_sec = refresh_sec
        self.record = Record.load(root_dir)
        self.thread = threading.Thread(target=self.update)
        self.thread.daemon = True
        self.thread.start()
        self.t_minus = 30

    def initialize(self):
        pass

    def get_timeline(self):
        return self.get_ohlcv()['time_utc']

    def get_symbols(self):
        return self.record.portfolio.symbols

    def get_config(self):
        return self.record.config

    def get_ohlcv(self):
        """
        Returns dictionary:
            {'close': 0.077,
             'high': 0.0773,
             'low': 0.0771,
             'open': 0.0772,
             'time_utc': Timestamp('2018-01-08 22:22:00'),
             'volume': 222.514}
        """
        return self.record.ohlcv.iloc[-self.t_minus:]

    def get_positions(self):
        positions = self.record.portfolio.positions
        return pd.DataFrame([p.to_dict() for p in positions])

    def get_positions_dct(self):
        positions = self.record.portfolio.positions
        dct = [p.to_dict() for p in positions]
        return dct #{p['asset']: p for p in dct}

    def get_performance(self):
        return self.record.portfolio.perf

    def get_pnl(self):
        periods = self.record.portfolio.perf.periods
        return pd.DataFrame([
            [p['end_time'], p['pnl']] for p in periods
        ], columns=['time_utc','pnl'])

    def get_returns(self):
        periods = self.record.portfolio.perf.periods
        return pd.DataFrame([
            [p['end_time'], p['returns']] for p in periods
        ], columns=['time_utc','returns'])

    def get_balance(self):
        cols = ['coin', 'free', 'used', 'total']
        balance = self.record.balance
        dct = balance.to_dict()
        return pd.DataFrame(
            data=[
                [c, dct[c]['free'], dct[c]['used'], dct[c]['total']]
                for c in balance.currencies],
            columns=cols
        )

    def get_orders(self):
        return self.record.orders

    def get_metrics(self):
        return self.record.metrics

    def refresh_data(self):
        self.record = Record.load(self.root_dir)

    def update(self):
        while True:
            self.refresh_data()
            time.sleep(self.refresh_sec)



data = RecordDataProvider(EXPERIMENT_PATH)
# print(data.get_config())
# print(data.get_symbols())
# print(data.get_metrics())
# print(data.get_positions())
# print(data.get_performance())
# print(data.get_balance())
# print(data.get_orders())
# print(data.get_ohlcv().head())
# #print(data.get_portfolio())
# print(data.get_ohlcv_dct().keys())

selected_dropdown_value = ['ETH/BTC']

app = dash.Dash()

app.layout = html.Div([
    html.Div([
        html.H1(EXPERIMENT_NAME, id='h1_title'),
        html.Div([
            dcc.Graph(
                id='ohlc',
                config={
                    'displayModeBar': False
                }
            ),
        ]),
        html.Div([
            dcc.Graph(
                id='v',
                config={
                    'displayModeBar': False
                }
            ),
        ]),
        html.Div([
            dcc.Graph(
                id='pnl',
                config={
                    'displayModeBar': False
                }
            ),
        ]),
        # html.Div([
        #     dcc.Graph(
        #         id='returns',
        #         config={
        #             'displayModeBar': False
        #         }
        #     ),
        # ], className="row"),
        html.Div([
            html.Div([
                html.H3(children='Positions'),
                html.Div(id='positions-table'),
            ]),
            html.Div([
                html.H3(children='Balance'),
                html.Div(id='balance-table'),
            ])
        ], className="two columns"),
        # html.Div([
        #     dcc.Graph(
        #         id='weights',
        #         config={
        #             'displayModeBar': False
        #         }
        #     ),
        # ], className="row"),
        dt.DataTable(
            rows=[{}], # initialise the rows
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id='positions-datatable'
        ),
        dcc.Interval(
            id='interval-component',
            interval=REFRESH_SEC*1000,
            n_intervals=0
        )
    ])
])
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(Output('ohlc', 'figure'),
              [Input('interval-component', 'n_intervals')])
def plot_olhc(n):
    global data
    ohlcv = data.get_ohlcv()
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
              [Input('interval-component', 'n_intervals')])
def plot_v(n):
    global data
    ohlcv = data.get_ohlcv()
    return {
        'data': [go.Bar(x=ohlcv['time_utc'],
                        y=ohlcv['volume'])],
        'layout': dict(title="Volume")
    }

@app.callback(Output('pnl', 'figure'),
              [Input('interval-component', 'n_intervals')])
def plot_pnl(n):
    global data
    pnl = data.get_pnl()
    return {
        'data': [go.Scatter(x=pnl['time_utc'],
                        y=pnl['pnl'], mode='lines')],
        'layout': dict(title="PnL")
    }


@app.callback(Output('positions-table', 'children'),
              [Input('interval-component', 'n_intervals')])
def plot_positions(n):
    global data
    df = data.get_positions()
    return generate_table(df)

@app.callback(Output('balance-table', 'children'),
              [Input('interval-component', 'n_intervals')])
def plot_balance(n):
    global data
    df = data.get_balance()
    return generate_table(df)

@app.callback(Output('positions-datatable', 'rows'),
              [Input('interval-component', 'n_intervals')])
def update_datatable(n):
    global data
    df = data.get_positions_dct()
    print(df)
    return df

def plot_weights(n):
    global data
    df = data.get_weights()
    return {
        'data': [go.Pie()],
        'layout': dict(title="Asset Allocation")
    }

app.run_server(port=8000, debug=True, host='0.0.0.0')
