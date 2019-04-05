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

print("")
print("Assuming things keep rolling along more or less as they have been, I")
print("predict, with 90% probability, that you'll receive between")
print(np.round(quantiles[0], 2), "and", np.round(quantiles[2], 2), "LBC",
      end=" ")
print("over the next month.")

plt.hist(future_tips, 500, density=True)
plt.xlabel("Future tips over next month (LBC)")
plt.ylabel("Probability Density")
plt.show()

