# If the Punisher traded crypto..

![alt text](docs/punisher.png "Logo Title Text 1")

## Quickstart

**Users**
* Run the demo.ipynb jupyter notebook

**Developers**
* Run developers.ipynb to see how various components interact

## Install


**Requirements:**
* Unix
* Anaconda3

**Install:**
```
conda install ipywidgets
jupyter nbextension enable --py --sys-prefix widgetsnbextension
conda install -c tim_shawver/label/dev qgrid==1.0.0b10
conda install -c conda-forge python.app
pip install -r requirements.txt
```

**Optional (model training):**
* PyTorch
* GPU (for training)
* CCXT / Twitter credentials (place in .env file)


## Config

* Open dotenv_example and rename .env
* Replace variables with your own values (GDAX, twitter)


**No API keys?** You can still download data with the Exchange APIs, just empty the dictionary we pass in as a config in ccxt.py

## Clients

* https://chrisjean.com/git-submodules-adding-using-removing-and-updating/

```
git submodule init
git submodule update
```

## Data

* https://www.dropbox.com/home/punisher
* https://www.quandl.com/collections/markets/bitcoin-data
* https://market.mashape.com/bravenewcoin/digital-currency-tickers
* https://bravenewcoin.com/
* https://coinmetrics.io/data-downloads/


## Resources

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
