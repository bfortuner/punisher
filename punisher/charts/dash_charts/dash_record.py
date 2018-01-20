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
import colorlover as cl

import punisher.config as cfg
import punisher.constants as c
from punisher.portfolio.asset import Asset
from punisher.feeds.ohlcv_feed import get_ohlcv_fpath
from punisher.charts.dash_viz import generate_table
from punisher.utils.dates import Timeframe, date_to_str

from punisher.charts.data_providers import RecordChartDataProvider


## Load Args

parser = argparse.ArgumentParser(description='Punisher Dash Vizualizer')
parser.add_argument('--name', help='name of your experiment', default='default')
parser.add_argument('--tminus',
                    help='Trailing # of records to include in chart',
                    default=sys.maxsize, type=int)
parser.add_argument('--refresh', help='How often to refresh the chart',
                    default=30, type=int)

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

app = dash.Dash()

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'
colorscale = cl.scales['9']['qual']['Paired']

assets = data.get_assets()
exchange_ids = ['All'] + data.get_exchange_ids()
benchmark_currencies = [c.BTC, c.USD]

app.layout = html.Div([
    html.H1(experiment_name),
    html.Div([
    html.Div([
        html.H2("OHLCV",
        style={'display': 'inline',
               'float': 'left',
               'font-size': '2.65em',
               'margin-left': '7px',
               'font-weight': 'bolder',
               'font-family': 'Product Sans',
               'color': "rgba(117, 117, 117, 0.95)",
               'margin-top': '20px',
               'margin-bottom': '0'
        }),
    ]),
    dcc.Dropdown(
        id='asset-ohlcv-input',
        options=[{'label': a.symbol, 'value': a.symbol} for a in assets],
        value=[assets[0].symbol],
        multi=True
    ),
    html.Div(id='graphs'),
    html.Div([
        html.Div([
            html.H2("Performance",
                style={
                'display': 'inline',
                'float': 'left',
                'font-size': '2.65em',
                'margin-left': '7px',
                'font-weight': 'bolder',
                'font-family': 'Product Sans',
                'color': "rgba(117, 117, 117, 0.95)",
                'margin-top': '20px',
                'margin-bottom': '0'
                }),
        ]),
        dcc.Dropdown(
            id='performance-input',
            options=[{'label': cur, 'value': cur}
                     for cur in benchmark_currencies],
            value=c.BTC,
            multi=False
        ),
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
        #     dcc.Graph(
        #         id='weights',
        #         config={
        #             'displayModeBar': False
        #         }
        #     ),
        # ]),
        html.Div([
            html.H2("Holdings",
                style={
                'display': 'inline',
                'float': 'left',
                'font-size': '2.65em',
                'margin-left': '7px',
                'font-weight': 'bolder',
                'font-family': 'Product Sans',
                'color': "rgba(117, 117, 117, 0.95)",
                'margin-top': '20px',
                'margin-bottom': '0'
                }),
        ]),
        dcc.Dropdown(
            id='holdings-input',
            options=[{'label': ex_id, 'value': ex_id}
                     for ex_id in exchange_ids],
            value='All',
            multi=False
        ),
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
], className="container")
])
# app.css.append_css({
#     'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# })
external_css = ["https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/2cc54b8c03f4126569a3440aae611bbef1d7a5dd/stylesheet.css"]

for css in external_css:
    app.css.append_css({"external_url": css})


def bbands(price, window_size=10, num_of_std=5):
    price = pd.Series(price)
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std  = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('asset-ohlcv-input', 'value'),
     Input('interval-component', 'n_intervals')])
def update_graph(symbols, n_intervals):
    graphs = []
    for i, symbol in enumerate(symbols):
        df = data.get_ohlcv()
        ex_id = c.PAPER
        candlestick = {
            'x': df.col('utc'),
            'open': df.col('open', symbol, ex_id),
            'high': df.col('high', symbol, ex_id),
            'low': df.col('low', symbol, ex_id),
            'close': df.col('close', symbol, ex_id),
            'type': 'candlestick',
            'name': symbol,
            'legendgroup': symbol,
            'increasing': {'line': {'color': colorscale[0]}},
            'decreasing': {'line': {'color': colorscale[1]}}
        }
        bb_bands = bbands(df.col('close', symbol, ex_id))
        bollinger_traces = [{
            'x': df.col('utc'), 'y': y,
            'type': 'scatter', 'mode': 'lines',
            'line': {'width': 1, 'color': colorscale[(i*2) % len(colorscale)]},
            'hoverinfo': 'none',
            'legendgroup': symbol,
            'showlegend': True if i == 0 else False,
            'name': '{} - bollinger bands'.format(symbol)
        } for i, y in enumerate(bb_bands)]
        graphs.append(dcc.Graph(
            id=symbol,
            figure={
                'data': [candlestick] + bollinger_traces,
                'layout': {
                    'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                    'legend': {'x': 0}
                }
            }
        ))

    return graphs


@app.callback(Output('pnl', 'figure'),
              [Input('interval-component', 'n_intervals')])
def plot_pnl(n):
    global data
    pnl = data.get_pnl()
    return {
        'data': [go.Scatter(x=pnl['utc'],
                        y=pnl['pnl'], mode='lines')],
        'layout': dict(title="PnL")
    }

@app.callback(Output('returns', 'figure'),
              [Input('interval-component', 'n_intervals')])
def plot_returns(n):
    global data
    returns = data.get_returns()
    return {
        'data': [go.Scatter(x=returns['utc'],
                        y=returns['returns'], mode='lines')],
        'layout': dict(title="Returns")
    }

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


if __name__ == "__main__":
    app.run_server(port=8000, debug=False, host='0.0.0.0')
