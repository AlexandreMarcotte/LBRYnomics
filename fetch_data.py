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
    DEPRECATED! Replaced by all_time_graph.py
    """
    print("all_claim_times is deprecated.")

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
        plt.xlabel("Time (days since LBRY began)")
        plt.ylabel("New claims added each day")
        subset = counts[-30:]
        plt.title("Recent average rate (last 30 days) = {n} claims per day.".\
                    format(n=int(subset.mean())))
        plt.gca().grid(True)
        plt.gca().tick_params(labelright=True)
#        plt.gca().set_yticks([1.0, 10.0, 100.0, 1000.0, 10000.0])
#        plt.gca().set_yticklabels(["1", "10", "100", "1000", "10000"])
        plt.legend()
        plt.savefig("claims.svg", bbox_inches="tight")
        print("Figure saved to claims.svg.")
        plt.show()

    return times


def view_count(url, auth_token):
    """
    A single view count
    """
    result = lbry.lbry_call("resolve", {"urls": [url]})
    claim_id = result[0][url]["claim_id"]
    url = "https://api.lbry.com/file/view_count?auth_token=" + auth_token + \
                "&" +\
                "claim_id=" + claim_id
    result = requests.get(url)
    return result.json()["data"][0]

def subscriber_counts(auth_token):
    """
    Get subscriber counts for all channels. Assumes a file output.csv
    exists which lists all channels with their name and claim_id.
    """

    import json
    import sqlite3

    # Open previous JSON
    f = open("subscriber_counts.json")
    old = json.load(f)
    f.close()

    # Create a dict from the old JSON, where the claim_id can return
    # the subscribers and the rank
    old_dict = {}
    for i in range(len(old["ranks"])):
        old_dict[old["claim_ids"][i]] = (old["subscribers"][i], old["ranks"][i])

    # Open claims.db
    db_file = "/home/brewer/local/lbry-sdk/lbry/lbryum-data/claims.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    query = "select claim_name, claim_id from claim where claim_type = 2;"
    vanity_names = []
    claim_ids = []
    subscribers = []

    # Iterate over query results
    i = 0
    for row in c.execute(query):
        vanity_names.append(row[0])
        claim_ids.append(row[1])
        i = i + 1
    conn.close()
    vanity_names = np.array(vanity_names)
    claim_ids = np.array(claim_ids)


    k = 0
    while True:
        """
        Go in batches of 100
        """
        # Cover a certain range of channels
        start = 100*k
        end = 100*(k+1)
        final = end >= len(claim_ids)
        if final:
            end = len(claim_ids)

        # Prepare the request to the LBRY API
        url = "https://api.lbry.com/subscription/sub_count?auth_token=" +\
                    auth_token + "&claim_id="
        for i in range(start, end):
            url += claim_ids[i] + ","
        url = url[0:-1] # No final comma

        # Do the request
        try:
            result = requests.get(url)
        except:
            print("Something went wrong")
            return

        # Get sub counts from the result and put them in the subscribers list
        result = result.json()
        for x in result["data"]:
            subscribers.append(x)
            i = len(subscribers)-1

        print("Processed {end} channels.".format(end=end))
        if final:
            break
        k += 1

    # Sort by number of subscribers then by vanity name.
    # Zip subs with name
    s_n = []
    indices = []
    for i in range(len(vanity_names)):
        s_n.append((subscribers[i], vanity_names[i]))
        indices.append(i)
    indices = sorted(indices, key=lambda x: (s_n[x][0], s_n[x][1]))[::-1]

    vanity_names = np.array(vanity_names)[indices]
    claim_ids = np.array(claim_ids)[indices]
    subscribers = np.array(subscribers)[indices]

    # Put the top 100 into the dict
    import datetime
    import json
    now = time.time()
    my_dict = {}
    my_dict["unix_time"] = now
    my_dict["human_time_utc"] = str(datetime.datetime.utcfromtimestamp(int(now))) + " UTC"
    my_dict["old_unix_time"] = old["unix_time"]
    my_dict["old_human_time_utc"] = old["human_time_utc"]
    my_dict["ranks"] = []
    my_dict["vanity_names"] = []
    my_dict["claim_ids"] = []
    my_dict["subscribers"] = []
    my_dict["change"] = []
    my_dict["rank_change"] = []

    for i in range(100):
        my_dict["ranks"].append(i+1)
        my_dict["vanity_names"].append(vanity_names[i])
        my_dict["claim_ids"].append(claim_ids[i])
        my_dict["subscribers"].append(int(subscribers[i]))

        # Compute subscribers change
        my_dict["change"].append(np.nan)
        my_dict["rank_change"].append(np.nan)
        try:
            my_dict["change"][-1] = int(subscribers[i]) - \
                                        old_dict[claim_ids[i]][0]
            my_dict["rank_change"][-1] = old_dict[claim_ids[i]][1] - \
                                            int(my_dict["ranks"][-1])
        except:
            pass


    f = open("subscriber_counts.json", "w")
    f.write(json.dumps(my_dict))
    f.close()



def view_counts(channel_name, auth_token, include_abandoned=False):

    # Get the channel's claim_id by doing a lbrynet resolve

    result = lbry.lbry_call("resolve", {"urls": [channel_name]})
    channel_claim_id = result[0][channel_name]["claim_id"]

    # For channels
    url = "https://api.lbry.com/subscription/sub_count?auth_token=" +\
                auth_token + "&" +\
                "claim_id=" + channel_claim_id
    result = requests.get(url)
    subscribers = result.json()["data"][0]

    # Get claim_ids from inside channel
    query = "SELECT name, claim_id, bid_state, valid_at_height, title FROM claim\
                WHERE publisher_id = '" + channel_claim_id + "'\n"
    if not include_abandoned:
        query += "AND bid_state <> 'Spent'"
    query += "ORDER BY release_time, created_at ASC;"



    query += "ORDER BY transaction_time ASC;"
    request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
    the_dict = request.json()

    view_counts = {}
    tot = 0
    view_counts_list = []
    for i in range(len(the_dict["data"])):
        claim_id = the_dict["data"][i]["claim_id"]
        url = "https://api.lbry.com/file/view_count?auth_token=" + auth_token + \
                    "&" +\
                    "claim_id=" + claim_id
        result = requests.get(url)

        name = str(the_dict["data"][i]["name"])
        views = result.json()["data"][0]
        view_counts[name] = views
        view_counts_list.append(views)
        tot += views
        message = "Claim {k}/{n} with name \""\
                    + name + "\" has {v} views."
        print(message.format(k=i+1,
                n=len(the_dict["data"]), v=views),
                flush=True)

    return { "view_counts": view_counts,
             "view_counts_vector": np.array(view_counts_list),
             "total_views": tot,
             "subscribers": subscribers }


def data_to_yaml(channel_name, yaml_file="data.yaml", plot=False):
    """
    Fetch all the tips at channel_name and write their data to
    Data/channel_name.yaml.
    Time units are months. Optionally, plot the tip history.
    """

    # Get the channel's claim_id by doing a lbrynet resolve

    result = lbry.lbry_call("resolve", {"urls": [channel_name]})
    channel_claim_id = result[0][channel_name]["claim_id"]

    # The SQL query to perform
    # NB: The use of the claim_address and the address_list from the output
    # table is to try to only capture tips (not other supports). This also
    # will not capture tips sent to the channel itself.
    query = "SELECT support.id as support_id, support.support_amount amount, transaction.transaction_time time\
                FROM claim\
                INNER JOIN support ON support.supported_claim_id = claim.claim_id\
                INNER JOIN transaction ON support.transaction_hash_id = transaction.hash\
                INNER JOIN output ON transaction.hash = output.transaction_hash \
                WHERE publisher_id = '" + channel_claim_id + "'\
                  AND output.address_list LIKE CONCAT('%25', claim_address, '%25')\
                  AND transaction.hash <> 'e867afabfa52bea6d5af84e65865dd5d0382c340646f1578192768033be48924'\
                GROUP BY support.id, support.support_amount, support.created_at"

    request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
    the_dict = request.json()
#    print(request.json())
#    exit()

    amounts = []
    times   = []
    for i in range(len(the_dict["data"])):
        amounts.append(float(the_dict["data"][i]["amount"]))
        times.append(float(the_dict["data"][i]["time"]) + rng.rand())


    # Get tips sent to channel itself
    query = "SELECT support.id as support_id, support.support_amount amount, transaction.transaction_time time\
                FROM claim\
                INNER JOIN support ON support.supported_claim_id = claim.claim_id\
                INNER JOIN transaction ON support.transaction_hash_id = transaction.hash\
                INNER JOIN output ON transaction.hash = output.transaction_hash \
                WHERE support.supported_claim_id = '" + channel_claim_id + "'\
                  AND output.address_list LIKE CONCAT('%25', claim_address, '%25')\
                  AND transaction.hash <> 'e867afabfa52bea6d5af84e65865dd5d0382c340646f1578192768033be48924'\
                GROUP BY support.id, support.support_amount, support.created_at"

    request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
    the_dict = request.json()
    for i in range(len(the_dict["data"])):
        amounts.append(float(the_dict["data"][i]["amount"]))
        times.append(float(the_dict["data"][i]["time"]) + rng.rand())

    amounts = np.array(amounts)
    times = np.array(times)

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
            plt.plot([times[i], times[i]], [0.0, amounts[i]], "b-", alpha=0.2)
        plt.ylim(bottom=0.0)
        t_range = t_end - t_start
        plt.xlim(t_start - 0.01*t_range, t_end)
        plt.xlabel("Time (unix time, months)", fontsize=12)
        plt.ylabel("Tip amount (LBC)", fontsize=12)
        plt.title("Tip history for " + channel_name.replace("#", "\#") +\
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


