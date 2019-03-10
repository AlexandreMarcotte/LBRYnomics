import pandas as pd

# Load exported CSV file
data = pd.read_csv("lbry-transactions-history.csv")

# Tips received
tips = (data["type"] == "tip") & (data["amount"] > 0.0)
subset = data.loc[tips, :]

# Oldest first
subset = subset.iloc[::-1, :]

# Extract times, converting units to days
ts = subset["timestamp"]/86400.0
amounts = subset["amount"]

import matplotlib.pyplot as plt
plt.plot(ts, amounts, "o-")
plt.show()

