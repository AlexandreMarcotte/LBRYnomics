"""
A model made of pulses.
"""

import matplotlib.pyplot as plt
import numpy as np
import numpy.random as rng

reps = 100

t = np.linspace(-100.0, 100.0, 10001)
duration = t.max() - t.min()

for rep in range(reps):

    while True:
        num_pulses = rng.randint(100)
        if rng.rand() <= 1.0/(1.0 + num_pulses):
            break

    # Flat background level is unity
    y = 1.0 + np.zeros(t.shape)

    # Hyperparameters
    mu_A = np.exp(3.0*rng.randn())
    sig_ln_A = 3.0*rng.rand()

    mu_L = 0.1*duration*np.exp(3.0*rng.randn())
    sig_ln_L = 3.0*rng.rand()

    for i in range(num_pulses):

        # Add pulses
        A = mu_A*np.exp(sig_ln_A*rng.randn())
        t0 = t.min() + (t.max() - t.min())*rng.rand()
        L = mu_L*np.exp(sig_ln_L*rng.randn())
        y[t > t0] += A*np.exp(-(t[t > t0] - t0)/L)

    plt.plot(t, y)
    plt.ylim([0.0, 1.1*y.max()])
    plt.show()

