# Punisher Bot

If the Punisher traded crypto..

## Requirements

* Unix
* Anaconda3
* PyTorch
* GPU (for training)
* GDAX / Twitter credentials (request .env file)
* Other libraries
* QGrid - https://github.com/quantopian/qgrid

```
conda install ipywidgets
jupyter nbextension enable --py --sys-prefix widgetsnbextension
conda install -c tim_shawver/label/dev qgrid==1.0.0b10
conda install graphviz
conda create --name catalyst python=2.7 scipy zlib
source activate catalyst

pip install -r requirements.txt
```

## Config

* Create an external directory to store your data inside (ask for data)
* Ask for .env file template
* Replace .env variables with your own values (GDAX, twitter, etc)

## Clients

* https://chrisjean.com/git-submodules-adding-using-removing-and-updating/

```
git submodule init
git submodule update
```

### GDAX

If you don't have credentials use this client:

```
gdax_client = gdax.PublicClient()
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
