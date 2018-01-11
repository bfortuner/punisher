import os
import sys
import time
import datetime
from collections import deque

import argparse

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


from charts.dash_viz import generate_table
from utils.dates import Timeframe, date_to_str

from charts.data_providers import RecordChartDataProvider


## Load Args

parser = argparse.ArgumentParser(description='Punisher Dash Vizualizer')
parser.add_argument('--name', help='name of your experiment', default='default')
parser.add_argument('--tminus',
                    help='Trailing # of records to include in chart',
                    default=sys.maxsize, type=int)
parser.add_argument('--refresh', help='How often to refresh the chart',
                    default=5, type=int)

args = parser.parse_args()
experiment_name = args.name
tminus = args.tminus
refresh_sec = args.refresh
root_dir = os.path.join(cfg.DATA_DIR, experiment_name)

print("Experiment: ", experiment_name)
print("Root: ", root_dir)
print("Tminus: ", tminus)
print("Refresh Sec: ", refresh_sec)


data = RecordChartDataProvider(root_dir, refresh_sec, tminus)
data.initialize()

selected_dropdown_value = ['ETH/BTC']

app = dash.Dash()

app.layout = html.Div([
    html.Div([
        html.H1(experiment_name, id='h1_title'),
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
        html.Div([
            dcc.Graph(
                id='returns',
                config={
                    'displayModeBar': False
                }
            ),
        ]),
        # html.Div([
        #     html.Div([
        #         html.H3(children='Positions'),
        #         html.Div(id='positions-table'),
        #     ]),
        #     html.Div([
        #         html.H3(children='Balance'),
        #         html.Div(id='balance-table'),
        #     ])
        # ]),
        # html.Div([
        #     dcc.Graph(
        #         id='weights',
        #         config={
        #             'displayModeBar': False
        #         }
        #     ),
        # ], className="row"),
        html.H3("Balance", id='balance_dt_title'),
        html.Div([
            dt.DataTable(
                rows=[{}], # initialise the rows
                row_selectable=False,
                filterable=False,
                sortable=True,
                selected_row_indices=[],
                id='balance-datatable'
            ),
        ]),
        html.H3("Positions", id='positions_dt_title'),
        html.Div([
            dt.DataTable(
                rows=[{}], # initialise the rows
                row_selectable=False,
                filterable=False,
                sortable=True,
                selected_row_indices=[],
                id='positions-datatable'
            ),
        ]),
        html.H3("Orders", id='orders_dt_title'),
        html.Div([
            dt.DataTable(
                rows=[{}], # initialise the rows
                row_selectable=False,
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                id='orders-datatable'
            ),
        ]),
        dcc.Interval(
            id='interval-component',
            interval=refresh_sec*1000,
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

@app.callback(Output('returns', 'figure'),
              [Input('interval-component', 'n_intervals')])
def plot_returns(n):
    global data
    returns = data.get_returns()
    return {
        'data': [go.Scatter(x=returns['time_utc'],
                        y=returns['returns'], mode='lines')],
        'layout': dict(title="Returns")
    }

# @app.callback(Output('positions-table', 'children'),
#               [Input('interval-component', 'n_intervals')])
def plot_positions(n):
    global data
    df = data.get_positions()
    return generate_table(df)

# @app.callback(Output('balance-table', 'children'),
#               [Input('interval-component', 'n_intervals')])
def plot_balance(n):
    global data
    df = data.get_balance()
    return generate_table(df)

#https://github.com/plotly/dash-table-experiments
@app.callback(Output('balance-datatable', 'rows'),
              [Input('interval-component', 'n_intervals')])
def update_balance_datatable(n):
    global data
    return data.get_balance_dct()

@app.callback(Output('positions-datatable', 'rows'),
              [Input('interval-component', 'n_intervals')])
def update_positions_datatable(n):
    global data
    return data.get_positions_dct()

@app.callback(Output('orders-datatable', 'rows'),
              [Input('interval-component', 'n_intervals')])
def update_orders_datatable(n):
    global data
    dct = data.get_orders_dct()
    return dct

def plot_weights(n):
    global data
    df = data.get_weights()
    return {
        'data': [go.Pie()],
        'layout': dict(title="Asset Allocation")
    }

app.run_server(port=8000, debug=True, host='0.0.0.0')
