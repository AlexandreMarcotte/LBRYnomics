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


def all_claim_times(plot=False):
    """
    Get the timestamps of all claims and plot the cumulative number vs. time!
    """

    # The SQL query to perform
    query = "SELECT transaction.transaction_time time\
             FROM\
                 claim\
                 INNER JOIN transaction\
                 ON claim.transaction_hash_id = transaction.hash\
             ORDER BY time ASC;"

    # Get all claims from the channel
    request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
    the_dict = request.json()

    times = np.empty(len(the_dict["data"]))
    for i in range(len(times)):
        times[i] = the_dict["data"][i]["time"]

    # Remove pending ones
    times = times[times >= 1E9]

    if plot:
        import matplotlib.pyplot as plt
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["font.size"] = 14
        plt.rc("text", usetex=True)

        plt.figure(figsize=(15, 10))

        plt.subplot(2, 1, 1)
        times_in_days = (times - times.min())/86400.0
        plt.plot(times_in_days,
                    np.arange(len(times)), "k-", linewidth=1.5)
        plt.ylabel("Cumulative number of claims")
        plt.title("Total number of claims = {n}.".format(n=len(times)))
        plt.xlim([0.0, times_in_days.max()])
        plt.ylim(bottom=-100)
        plt.gca().grid(True)
        plt.gca().tick_params(labelright=True)



        plt.subplot(2, 1, 2)
        # Integers
        days = times_in_days.astype("int64")
        bin_width = 1.0
        bins = np.arange(0, np.max(days)+1) - 0.5*bin_width # Bin edges including right edge of last bin
        counts = plt.hist(days, bins, alpha=0.5, color="g", label="Raw",
                            width=bin_width, align="mid")[0]

        # Compute 10-day moving average
        moving_average = np.zeros(len(bins)-1)
        for i in range(len(moving_average)):
            subset = counts[0:(i+1)]
            if len(subset) >= 10:
                subset = subset[-10:]
            moving_average[i] = np.mean(subset)
        plt.plot(bins[0:-1] + 0.5*bin_width, moving_average, "k-",
                    label="10-day moving average", linewidth=1.5)
#        plt.gca().set_yscale("log")
        plt.xlim([0.0, times_in_days.max()])
        plt.xlabel("Time (days)")
        plt.ylabel("New claims added each day")
        subset = counts[-30:]
        plt.title("Recent rate (last 30 days) = {n} claims per day.".\
                    format(n=int(subset.mean())))
        plt.gca().grid(True)
        plt.gca().tick_params(labelright=True)
#        plt.gca().set_yticks([1.0, 10.0, 100.0, 1000.0, 10000.0])
#        plt.gca().set_yticklabels(["1", "10", "100", "1000", "10000"])
        plt.legend()
        plt.savefig("claims.svg", bbox_inches="tight")
        print("Figure saved to claims.svg.")

    return times


def data_to_yaml(channel_name, yaml_file="data.yaml", plot=False):
    """
    Fetch all the tips at channel_name and write their data to
    Data/channel_name.yaml.
    Time units are months. Optionally, plot the tip history.
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

#    # Get beginning time
#    # The SQL query to perform
#    query = "SELECT transaction_time FROM claim\
#                 WHERE publisher_id = '" + channel_claim_id + "';"

#    # Get all claims from the channel (used for t_start)
#    request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
#    the_list = request.json()["data"]

#    claim_times = np.empty(len(the_list))
#    for i in range(len(the_list)):
#        claim_times[i] = float(the_list[i]["transaction_time"]) + rng.rand()
#    t_start = claim_times.min()

    # Remove anything from before a unix time of around 500 months -
    # it's likely an
    # unconfirmed tip, which has early time.
    keep = times >= 1E9
    times = times[keep]
    amounts = amounts[keep]

    t_start = times.min()
    t_end = time.time()

    # Convert all times to months
    t_start /= 2629800.0
    t_end /= 2629800.0
    times /= 2629800.0

    # Save to a YAML file
    filename = "Data/" + channel_name + ".yaml"
    f = open(filename, "w")
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

    # Now, put a link to the data in data.yaml
    f = open("data.yaml", "w")
    f.write("# Just a pointer to the dataset to be loaded by main\n---\n")
    f.write("src: \"" + filename + "\"\n")
    f.close()

    print("Output written to {file}.".format(file=filename))


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
        t_range = t_end - t_start
        plt.xlim(t_start - 0.01*t_range, t_end)
        plt.xlabel("Time (unix time, months)", fontsize=12)
        plt.ylabel("Tip amount (LBC)", fontsize=12)
        plt.title("Tip history for " + channel_name +\
                    ". Total = {tot} LBC."\
                    .format(tot=np.round(np.sum(amounts), 2)),
                    fontsize=14)
        plt.show()


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2:
        channel = sys.argv[1]
        data_to_yaml(channel, plot=True)
    else:
        all_claim_times(plot=True)


