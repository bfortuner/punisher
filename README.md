# My Man

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

## APIs

### GDAX

If you don't have credentials use this client:

```
gdax_client = gdax.PublicClient()
```