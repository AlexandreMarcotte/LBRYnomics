import numpy as np
import pandas as pd

# Load exported CSV file
data = pd.read_csv("lbry-transactions-history.csv")

# Tips received
tips = (data["type"] == "tip") & (data["amount"] > 0.0)
subset = data.loc[tips, :]

# Oldest first
subset = subset.iloc[::-1, :]

# Extract times, converting units to days
ts = np.array(subset["timestamp"]/86400.0)
amounts = np.array(subset["amount"])

# Open output file
f = open("lbry-transactions-history.yaml", "w")

# t_start and t_end in the model were supposed to be the publication time
# of a single claim and the current time respectively, so this isn't right,
# because this script is only looking at tip times.
t_start = ts.min()
t_end   = ts.max()

f.write("# YAML data about tips received.\n---\n")
f.write("t_start: " + str(t_start) + "\n")
f.write("t_end: "   + str(t_end)   + "\n")

f.write("times:\n")
for i in range(len(ts)):
    f.write("    - " + str(ts[i]) + "\n")

f.write("amounts:\n")
for i in range(len(ts)):
    f.write("    - " + str(amounts[i]) + "\n")

f.close()

