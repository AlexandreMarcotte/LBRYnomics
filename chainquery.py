# Trying to use chainquery
from pprint import pprint
import requests
import urllib.request

# Channel name
channel_name = "@BrendonBrewer"

# Get the channel's claim_id by doing a lbrynet resolve
from fetch_data import lbry
result = lbry.lbry_call("resolve", {"urls": [channel_name]})
channel_claim_id = result[0][channel_name]["certificate"]["claim_id"]

# The SQL query to perform
query = "SELECT support_amount amount, transaction.transaction_time time FROM\
            claim\
            INNER JOIN support\
            ON claim.claim_id = support.supported_claim_id\
            INNER JOIN transaction\
            ON support.transaction_hash_id = transaction.hash\
            WHERE publisher_id = '" + channel_claim_id + "';"

# Get all claims from the channel
request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
the_dict = request.json()

if the_dict["success"]:

    import matplotlib.pyplot as plt
    import numpy as np

    amounts = np.empty(len(the_dict["data"]))
    times   = np.empty(len(the_dict["data"]))
    for i in range(len(times)):
        amounts[i] = float(the_dict["data"][i]["amount"])
        times[i]   = float(the_dict["data"][i]["time"])

    plt.plot(times, amounts, "o")
    plt.ylim(bottom=0.0)
    plt.show()

