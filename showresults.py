import dnest4.classic as dn4
import matplotlib.pyplot as plt
import numpy as np
import yaml

# Postprocess DNest4 output
dn4.postprocess()

# Load the data
f = open("data.yaml")
data = yaml.load(f, Loader=yaml.SafeLoader)
f.close()

# Plot the forecast
posterior_sample = dn4.my_loadtxt("posterior_sample.txt")
amount = posterior_sample[:,-1]
amount = np.sort(amount)
n = len(amount)
indices = [ int(0.1*n), int(0.5*n), int(0.9*n) ]
tip_rate = amount/(data["t_end"] - data["t_start"])*1000.0
quantiles = tip_rate[indices]

print("Future tip rate (10%, 50%, 90% quantiles): ",
      np.round(quantiles, 2), "LBC per 1000 blocks.")

plt.hist(tip_rate, 100)
plt.xlabel("Future tip rate (LBC per 1000 blocks)")
plt.show()

