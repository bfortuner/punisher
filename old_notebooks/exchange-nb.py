from exchanges.exchange import *
import constants as c

print(c.PAPER)
print(c.GDAX)
# Simulation with live data from GDAX
config = {"data_provider_name": c.GDAX}

ex = load_exchange(c.PAPER, config)

print(ex.id)
