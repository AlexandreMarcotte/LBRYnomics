import dnest4.classic as dn4
import matplotlib.pyplot as plt

# Postprocess DNest4 output
dn4.postprocess()

# Plot the forecast
posterior_sample = dn4.my_loadtxt("posterior_sample.txt")
amount = posterior_sample[:,-1]
print("Future tips =", amount.mean(), "+-", amount.std(), "LBC.")

plt.hist(posterior_sample[:,-1], 100)
plt.xlabel("Future tips")
plt.show()

