# My, Man!

![alt text](docs/punisher.png "Logo Title Text 1")

## Quickstart

1. Download price data from S3

```
python -m punisher.data.ohlcv_fetcher --exchange binance --symbol ETH/BTC --timeframe 30m --action download
```

2. Run the strategy script in backtesting mode
```
python -m punisher.strategies.simple -ohlcv .data/binance_ETH_BTC_30m.csv -t 30m -m backtest -a ETH/BTC -ex binance
```

3. View the results (visit localhost:8000)
```
python -m punisher.charts.dash_charts.dash_record --name default_backtest
```

## Install

1. Install [Miniconda](https://conda.io/miniconda.html) with Python 3.6

2. Create conda environment
```
conda env create -f environment.yaml -n punisher
source activate punisher
```
3. Add your API keys to ```dotenv_example``` and rename ```.env```.

**No API keys?**
You can still download data from our S3 bucket for backtesting. Or access the Exchange public APIs by emptying the dictionary we pass in as a config to the CCXTExchange class.

4. Install Extras (Optional)
```
conda install ipywidgets
jupyter nbextension enable --py --sys-prefix widgetsnbextension
conda install -c tim_shawver/label/dev qgrid==1.0.0b10
conda install -c conda-forge python.app
conda install pytorch torchvision -c pytorch (http://pytorch.org/)
```

## Download data from S3

OHLCV
```
python -m punisher.data.ohlcv_fetcher --exchange gdax --symbol BTC/USD --timeframe 1d --action download
```

Reddit
```
python -m punisher.data.reddit_fetcher --subreddit bitcoin --action download
```

Twitter
```
python -m punisher.data.tweet_fetcher --query 'bitcoin OR btc' --lang en --action download
```

## Running Tests
```
python -m pytest tests/ (all tests)
python -m pytest -k filenamekeyword (tests matching keyword)
python -m pytest tests/utils/test_sample.py (single test file)
python -m pytest tests/utils/test_sample.py::test_answer_correct (single test method)
python -m pytest --resultlog=testlog.log tests/ (log output to file)
python -m pytest -s tests/ (print output to console)
```

## How to commit (cleanly)

1. Before coding:

```
git pull master
git checkout -b feature
```

2. After coding, when you're ready to merge
```
# Pull latest changes from repo
git checkout master
git pull

# Merge master into feature branch.
git checkout feature
git merge master
```

3. Resolve conflicts

4. Merge feature into master and squash all your commits
```
git checkout master
git merge feature --squash
git commit -m 'Detailed Commit message describing your changes'
git push
```

## Resources

### Data

* https://www.quandl.com/collections/markets/bitcoin-data
* https://market.mashape.com/bravenewcoin/digital-currency-tickers
* https://bravenewcoin.com/
* https://coinmetrics.io/data-downloads/


### Exchanges

* https://www.coinigy.com
* https://poloniex.com
* https://www.gdax.com/
* https://gemini.com/
* https://www.binance.com/
* https://www.kraken.com/

### Research

* https://arxiv.org/archive/q-fin

### Tutorials

* [Buy/Sell/Short on Poloneix](https://www.youtube.com/watch?v=YwmoHfZ-qm8)

### Blogs/News

* TODO

### Tools / Charts

* https://zeroblock.com/
* https://www.tradingview.com/

### Repos

* https://github.com/Crypto-AI/Gemini
* https://github.com/quantopian/qgrid

### Known Issues

* [TODO](TODO.md)
