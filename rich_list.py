import fetch_data
import numpy as np
import pandas as pd
import showresults
import subprocess
import yaml

# List of channels to make forecasts for
data = pd.read_csv("channels.csv")
channels = []
for i in range(data.shape[0]):
    if data.iloc[i, 0][0] == "@":
        channels.append(data.iloc[i, 0] + "#" +  data.iloc[i, 1])
channels = sorted(channels, key=lambda s: s.lower())

import sys

# Open output CSV file
f = open("rich_list.csv", "w")
f.write("channel_name,months_since_first_tip,num_tips,lbc_received,lbc_per_month\n")
f.flush()

for channel in channels:
    try:
        fetch_data.data_to_yaml(channel)

        yaml_file = open("data.yaml")
        data = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        src = data["src"]
        yaml_file.close()
        yaml_file = open(src)
        data = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        yaml_file.close()

        f.write(channel + ",")
        duration = data["t_end"] - data["t_start"]
        f.write(str(np.round(duration, 2)) + ",")

        tot = 0.0
        if data["amounts"] is not None and len(data["amounts"]) > 0:
            for amount in data["amounts"]:
                tot += float(amount) # Sometimes yaml thinks it's a string

        f.write(str(len(data["amounts"])) + ",")
        f.write(str(np.round(tot, 2)) + ",")
        f.write(str(np.round(tot/duration, 2)) + ",")

        f.write("\n")
        f.flush()

    except:
        pass

f.close()

