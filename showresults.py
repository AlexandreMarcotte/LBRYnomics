import dnest4.classic as dn4
import matplotlib.pyplot as plt
import numpy as np

# Postprocess DNest4 output
dn4.postprocess()

# Plot the forecast
posterior_sample = dn4.my_loadtxt("posterior_sample.txt")
amount = posterior_sample[:,-1]
amount = np.sort(amount)
n = len(amount)
indices = [ int(0.1*n), int(0.5*n), int(0.9*n) ]
quantiles = amount[indices]

print("Future tips (10%, 50%, 90% quantiles):", np.round(quantiles, 2))

plt.hist(posterior_sample[:,-1], 100)
plt.xlabel("Future tips")
plt.show()

