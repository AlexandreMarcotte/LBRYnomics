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
amounts = mu_tips*np.exp(sig_log_tips*rng.randn(num_tips))

# Save data as YAML
f = open("example_data.yaml", "w")
f.write("---\n")
f.write("publish_time: " + str(publish_time) + "\n")
f.write("current_time: " + str(current_time) + "\n")
f.write("times:\n")
for i in range(num_tips):
    f.write("    - " + str(ts[i]) + "\n")
f.write("amounts:\n")
for i in range(num_tips):
    f.write("    - " + str(amounts[i]) + "\n")
f.close()

# Plot tips
plt.bar(ts, amounts, align="center", width=0.3)
plt.xlabel("Time (daamounts)")
plt.ylabel("Amount (LBC)")
plt.show()

