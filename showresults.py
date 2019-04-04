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
future_tips = amount
quantiles = future_tips[indices]

print("Total tips forecast over next 10,000 blocks: (10%, 50%, 90% quantiles): ",
      np.round(quantiles, 2), "LBC.")

plt.hist(future_tips, 500, density=True)
plt.xlabel("Future tips over next 10,000 blocks (LBC)")
plt.ylabel("Probability Density")
plt.show()

