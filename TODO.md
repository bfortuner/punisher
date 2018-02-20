# TODO

### Research

* Explore papers / projects using twitter for sentiment, news analysis on stocks/crypto
* Explore machine learning research / projects for price prediction, portfolio optimization, and news/event

### Exchanges

* CCXT GDAX fails to parse orders if filled is None. https://github.com/ccxt/ccxt/issues/1448

### Balance

* Verify starting_cash <= actual balance on Live Exchange

### Data / Feeds

* BUG: Data feed re-downloads all data every feed.next() iteration
* BUG: Simulate does not check for None after call feed.next()
* Update `ohlcv_fetcher.py` to clean up local copies of files and aggregate all subfiles into one file per asset.
* Method to check for NaN values and missing timesteps in data feed. And method to fill these values with the known value(pd.fillna('ffill'))
* Add Brave New Coin data provider and start downloading data with ohlcv_fetcher
* Update live feed to initialize with historical data, but start vending data at present time.

### Record

* How to store multiple runs of the same strategy with different hyperparameters? Right now we will override previous experiment run.

### Strategies

* Create example strategy files
  * Buy/Hold
  * Momentum (SMA)
  * Mean Reversion
  * Multiple Assets
  * Portfolio optimization
  * Exchange Arbitrage

### Machine Learning

* Add example notebooks in PyTorch
  * RNN
  * LSTM
  * Conv LSTM
  * Reinforcement Learning

### Ordering

* Cancel orders 0% filled after new timestep reached with no fill
* Add method rebalancePortfolio(assets, weights) to OrderManager which places the necessary buy/sell orders to rebalance a portfolio provided a list of weights (Portfolio Optimization)
* Add margin ordering + accounts

### Portfolio

* Update Position to take an exchange_id
* Refactor Portfolio and Performance to account for positions across exchanges

### Trading

* Create fees model for paper exchange
* Create slippage model for paper exchange
* Add margin ordering + accounts

### Dash Visualizations

* Plot Buy/Sell orders chart
* Launch Dash inside the Strategy Script (separate thread)
* Plot Cash levels line chart
* Plot portfolio allocation bar chart (position weights)
* Dropdown to set Exchange for OHLCV pricing chart (when multiple exchange price data in feed)
* Plot balance by coin bar chart
* Plot "benchmark" PnL/Returns (provided by user)
* Create a multi-page Dash app where we can view multiple strategies running (stop/start/pause them)

### Indicators / Metrics

* SMA (Simple Moving Average method)
* Bolinger Bands

### Testing

* Test full trading lifecycle (backtest, sim, live)
* Test Canceling orders

### Known Issues / Bugs

* Fetching historical data using 1m period only goes back 1 day and may cause bugs when using start/end
