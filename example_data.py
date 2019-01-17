"""
Generate example data.
"""

import matplotlib.pyplot as plt
import numpy as np
import numpy.random as rng

# Seed the RNG
rng.seed(0)

# Publication time and current time
t_start = 2.2
t_end = 100.7
duration = t_end - t_start

# True parameter values
lambda_tips = 0.5
mu_tips = 1.0
sig_log_tips = 1.9

# Arrival times of tips from poisson process
expected_num_tips = lambda_tips*duration
num_tips = rng.poisson(expected_num_tips)

# Uniform distribution for times given number 
times = t_start + duration*rng.rand(num_tips)
times = np.sort(times)

# Amounts of tips
amounts = mu_tips*np.exp(sig_log_tips*rng.randn(num_tips))

# Save data as YAML
f = open("example_data.yaml", "w")
f.write("---\n")
f.write("t_start: " + str(t_start) + "\n")
f.write("t_end: " + str(t_end) + "\n")
f.write("times:\n")
for i in range(num_tips):
    f.write("    - " + str(times[i]) + "\n")
f.write("amounts:\n")
for i in range(num_tips):
    f.write("    - " + str(amounts[i]) + "\n")
f.close()

# Plot tips
def plot_peaks(ts, ys, color="k", alpha=0.3):
    """
    Like a bar plot but with lines.
    """
    assert len(ts) == len(ys)
    for i in range(len(ts)):
        plt.plot([ts[i], ts[i]], [0.0, ys[i]], "-", color=color, alpha=alpha)
    plt.ylim([0.0, 1.05*np.max(ys)])

plot_peaks(times, amounts)
#plt.bar(times, amounts, align="center", width=0.3)
plt.xlabel("Time (days)")
plt.ylabel("Amount (LBC)")
plt.show()

