from exchanges.exchange import *
import constants as c

print(ex_cfg.PAPER)
print(ex_cfg.GDAX)
# Simulation with live data from GDAX
config = {"data_provider_name": ex_cfg.GDAX}

ex = load_exchange(ex_cfg.PAPER, config)

print(ex.id)
