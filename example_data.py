"""
Generate example data.
"""

import matplotlib.pyplot as plt
import numpy as np
import numpy.random as rng

# Seed the RNG
rng.seed(0)

# Publication time and current time
publish_time = 2.2
current_time = 100.7
duration = current_time - publish_time

# True parameter values
lambda_tips = 0.5
mu_tips = 1.0
sig_log_tips = 0.3

# Arrival times of tips from poisson process
expected_num_tips = lambda_tips*duration
num_tips = rng.poisson(expected_num_tips)

# Uniform distribution for times given number 
ts = publish_time + duration*rng.rand(num_tips)
ts = np.sort(ts)

# Amounts of tips
ys = mu_tips*np.exp(sig_log_tips*rng.randn(num_tips))

# Save data
data = np.empty((num_tips, 2))
data[:,0] = ts
data[:,1] = ys
np.savetxt("example_data.txt", data)

# Plot tips
plt.bar(ts, ys, align="center", width=0.3)
plt.xlabel("Time (days)")
plt.ylabel("Amount (LBC)")
plt.show()

