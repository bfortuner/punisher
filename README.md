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
```

## Config

* Create an external directory to store your data inside (ask for data)
* Ask for .env file template
* Replace .env variables with your own values (GDAX, twitter, etc)

## Clients

* https://chrisjean.com/git-submodules-adding-using-removing-and-updating/

### GDAX

If you don't have credentials use this client:

```
gdax_client = gdax.PublicClient()
```


## Data Sources

* https://www.dropbox.com/home/punisher
* https://www.quandl.com/collections/markets/bitcoin-data
* https://market.mashape.com/bravenewcoin/digital-currency-tickers
* https://bravenewcoin.com/
* https://coinmetrics.io/data-downloads/