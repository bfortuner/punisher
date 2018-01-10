import time
import threading

import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import numpy as np


class DashViz():
    def __init__(self, app):
        self.app = app
        # self.app = dash.App()
        # self.data = data
        # self.layout = layout
        #self.thread = threading.Thread(target=self._run_server)
        #self.thread.daemon = True
        self.css_url = 'https://codepen.io/chriddyp/pen/bWLwgP.css'

    # def run(self):
        # self.data.initialize()
        # self.app.layout = self.layout
        # self.app.css.append_css({'external_url': self.css_url})
        #self.thread.start()

    def run(self, port=8000, debug=True):
        self.app.run_server(
            port=port, debug=True,
            host='0.0.0.0')


class DashDataProvider():
    def __init__(self, refresh_sec):
        self.refresh_sec = refresh_sec
        self.thread = threading.Thread(target=self._update)
        #self.thread.daemon = True
        self.thread.start()

    def initialize(self):
        self.feed.initialize()

    def update(self):
        return NotImplemented

    def _update(self):
        while True:
            self.update()
            time.sleep(self.refresh_sec)


## Helpers

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )
