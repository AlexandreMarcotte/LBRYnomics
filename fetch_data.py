"""
Trying to use chainquery instead of the daemon to get all the data
I'm after.
"""

import ira
import numpy as np
import numpy.random as rng
import requests
import time
import urllib.request
import yaml

# Initialise one of these things
lbry = ira.lbryRPC()

def data_to_yaml(channel_name, yaml_file="data.yaml", plot=False):
    """
    Fetch all the tips at channel_name and write their data to
    data.yaml. Time units are months. Optionally, plot the tip history.
    """

    # Get the channel's claim_id by doing a lbrynet resolve

    result = lbry.lbry_call("resolve", {"urls": [channel_name]})
    channel_claim_id = result[0][channel_name]["certificate"]["claim_id"]

    # The SQL query to perform
    query = "SELECT support_amount amount, transaction.transaction_time time\
             FROM\
                 claim\
                 INNER JOIN support\
                 ON claim.claim_id = support.supported_claim_id\
                 INNER JOIN transaction\
                 ON support.transaction_hash_id = transaction.hash\
                 WHERE publisher_id = '" + channel_claim_id + "';"

    # Get all claims from the channel
    request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
    the_dict = request.json()

    # Test for success
    #if the_dict["success"]:

    amounts = np.empty(len(the_dict["data"]))
    times   = np.empty(len(the_dict["data"]))
    for i in range(len(times)):
        amounts[i] = float(the_dict["data"][i]["amount"])
        times[i]   = float(the_dict["data"][i]["time"]) + rng.rand()

    # Put amounts and times in time order
    indices = np.argsort(times)
    amounts = amounts[indices]
    times = times[indices]

    # Get beginning time
    # The SQL query to perform
    query = "SELECT transaction_time FROM claim\
                 WHERE publisher_id = '" + channel_claim_id + "';"

    # Get all claims from the channel (used for t_start)
    request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
    the_list = request.json()["data"]

    claim_times = np.empty(len(the_list))
    for i in range(len(the_list)):
        claim_times[i] = float(the_list[i]["transaction_time"]) + rng.rand()
    t_start = claim_times.min()
    t_end = time.time()


    # Convert all times to months
    t_start /= 2629800.0
    t_end /= 2629800.0
    times /= 2629800.0

    # Save to data.yaml
    f = open("data.yaml", "w")
    f.write("---\n")
    f.write("t_start: " + str(t_start) + "\n")
    f.write("t_end: "   + str(t_end) + "\n")

    f.write("times:\n")
    for t in times:
        f.write("    - " + str(t) + "\n")
    f.write("amounts:\n")
    for amount in amounts:
        f.write("    - " + str(amount) + "\n")

    f.close()
    print("Output written to data.yaml.")


    if plot:
        # Plot the tips
        import matplotlib.pyplot as plt

        plt.rcParams["font.family"] = "serif"
        plt.rcParams["font.size"] = 12
        plt.rc("text", usetex=True)

        plt.figure(figsize=(10, 5))
        for i in range(len(amounts)):
            plt.plot([times[i], times[i]], [0.0, amounts[i]], "b-", alpha=0.5)
        plt.ylim(bottom=0.0)
        plt.xlim(t_start, t_end)
        plt.xlabel("Time (unix time, months)", fontsize=12)
        plt.ylabel("Tip amount (LBC)", fontsize=12)
        plt.title("Tip history for " + channel_name, fontsize=14)
        plt.show()


if __name__ == "__main__":
    import sys

    channel = "@Lunduke" # A default channel
    if len(sys.argv) >= 2:
        channel = sys.argv[1]

    data_to_yaml(channel, plot=True)

