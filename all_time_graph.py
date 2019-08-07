"""
Get the timestamps of all claims and plot the cumulative number vs. time!
"""

import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import requests
import sqlite3
import time

def make_graph(mode, show=True):
    """
    mode must be "claims" or "channels"
    """
    if mode != "claims" and mode != "channels":
        return

    plt.close("all")

    # Open the DB
    db_file = "/home/brewer/local/lbry-sdk/lbry/lbryum-data/claims.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # List for results
    times = []

    # Query
    if mode == "claims":
        x = "<>"
    else:
        x = "="
    query = "SELECT creation_timestamp FROM claim\
                                  WHERE claim_type {x} 2;".format(x=x)

    # Iterate over query results
    i = 0
    for t in c.execute(query):
        times.append(t)
        i = i + 1

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

    # Sort the times and convert to a numpy array
    times = np.sort(np.array(times).flatten())

    # Save some stats to JSON for Electron
    now = time.time()
    my_dict = {}
    my_dict["unix_time"] = now
    my_dict["human_time_utc"] = str(datetime.datetime.utcfromtimestamp(int(now))) + " UTC"
    my_dict["total_{mode}".format(mode=mode)] = int(\
                len(times))
    my_dict["new_{mode}_1_hour".format(mode=mode)] = int(\
                np.sum(times > (now - 3600.0)))
    my_dict["new_{mode}_24_hours".format(mode=mode)] = int(\
                np.sum(times > (now - 86400.0)))
    my_dict["new_{mode}_7_days".format(mode=mode)] = int(\
                np.sum(times > (now - 7*86400.0)))
    my_dict["new_{mode}_30_days".format(mode=mode)] = int(\
                np.sum(times > (now - 30*86400.0)))
    f = open("{mode}_stats.json".format(mode=mode), "w")
    f.write(json.dumps(my_dict))
    f.close()

    # Count new claims this UTC day
    count_today = np.sum(times > 86400.0*int(now/86400.0))
    print("{K} {mode}, {n} from today (UTC). ".format(K=len(times), mode=mode, n=count_today), end="", flush=True)



    # Plotting stuff
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.size"] = 14
    plt.rc("text", usetex=True)

    plt.figure(figsize=(15, 11))
    plt.subplot(2, 1, 1)
    times_in_days = (times - 1483228800)/86400.0
    days = times_in_days.astype("int64")
    plt.plot(times_in_days,
                np.arange(len(times)), "k-", linewidth=1.5)
    plt.ylabel("Cumulative number of {mode}".format(mode=mode))
    plt.title("Total number of {mode} = {n}.".format(n=len(times), mode=mode))
    plt.xlim([0.0, days.max() + 1])
    plt.ylim(bottom=-100)
    plt.gca().grid(True)
    plt.gca().tick_params(labelright=True)

    plt.subplot(2, 1, 2)
    bin_width = 1.0

    # Bin edges including right edge of last bin
    bins = np.arange(0, np.max(days)+2) - 0.5*bin_width
    color = "g"
    if mode == "channels":
        color="b"
    counts = plt.hist(days, bins, alpha=0.5, color=color, label="Raw",
                        width=bin_width, align="mid")[0]

    # Compute 10-day moving average
    moving_average = np.zeros(len(bins)-1)
    for i in range(len(moving_average)):
        subset = counts[0:(i+1)]
        if len(subset) >= 10:
            subset = subset[-10:]
        moving_average[i] = np.mean(subset)
    plt.plot(bins[0:-2] + 0.5*bin_width, moving_average[0:-1], "k-",
                label="10-day moving average", linewidth=1.5)
    #        plt.gca().set_yscale("log")
    plt.xlim([0.0, days.max() + 1])
    plt.xlabel("Time (days since 2017-01-01)")
    plt.ylabel("New {mode}s added each day".format(mode=mode))
    subset = counts[-31:-1]
    plt.title("Recent average rate (last 30 days) = {n} {mode} per day.".\
                format(n=int(np.sum(time.time() - times <= 30.0*86400.0)/30.0),
                       mode=mode))
    plt.gca().grid(True)
    plt.gca().tick_params(labelright=True)
    #        plt.gca().set_yticks([1.0, 10.0, 100.0, 1000.0, 10000.0])
    #        plt.gca().set_yticklabels(["1", "10", "100", "1000", "10000"])
    plt.legend()

    plt.savefig("{mode}.svg".format(mode=mode), bbox_inches="tight")
    print("Figure saved to {mode}.svg.".format(mode=mode))
    if show:
        plt.show()

def aggregate_tips():
    """
    Calculate tips over past X amount of time and write JSON output
    """

    # The SQL query to perform
    now = time.time()
    print("Computing tip stats...", end="", flush=True)
    labels = ["30_days", "7_days", "24_hours", "1_hour"]
    windows = [30*86400.0, 7*86400.0, 1*86400.0, 3600.0]
    result = {}
    result["unix_time"] = now
    result["human_time_utc"] = str(datetime.datetime.utcfromtimestamp(int(now))) + " UTC"

    query = "SELECT support.id as support_id, support.support_amount amount,\
                            transaction.transaction_time time\
                FROM claim\
                INNER JOIN support ON support.supported_claim_id = claim.claim_id\
                INNER JOIN transaction ON support.transaction_hash_id = transaction.hash\
                INNER JOIN output ON transaction.hash = output.transaction_hash \
                WHERE output.address_list LIKE CONCAT('%25', claim_address, '%25')\
                      AND transaction.transaction_time > ({now} - {window})\
                      AND transaction.transaction_time <= {now}\
                GROUP BY support.id, support.support_amount, support.created_at"\
                    .format(now=now, window=windows[0])

    request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
    the_dict = request.json()

    # Get tips into numpy array
    times = []
    tips = []
    for row in the_dict["data"]:
        times.append(float(row["time"]))
        tips.append(float(row["amount"]))
    times = np.array(times)
    tips = np.array(tips)

    for i in range(len(labels)):
        keep = times > (now - windows[i])
        times = times[keep]
        tips = tips[keep]
        result["num_tips_{label}".format(label=labels[i])] = len(tips)
        result["lbc_tipped_{label}".format(label=labels[i])] = float(tips.sum())
        result["biggest_tip_{label}".format(label=labels[i])] = float(tips.max())

    f = open("tips_stats.json", "w")
    f.write(json.dumps(result))
    f.close()
    print("done.")
    return(result)


def publish_files():
    """
    Publish files to somewhere on the internet.
    """
    print("Publishing files to the internet...", end="", flush=True)
    from subprocess import STDOUT, check_output
    output = check_output("./upload.sh", stderr=STDOUT, timeout=30.0)
    print("done.")
    return output


if __name__ == "__main__":

    # Do it manually once then enter the infinite loop
    now = time.time()
    print("The time is " + str(datetime.datetime.utcfromtimestamp(int(now))) + ".")
    make_graph("claims")
    make_graph("channels")
    aggregate_tips()

    import os
    try:
        publish_files()
    except:
        pass
    import time
    while True:
        print("", flush=True)
        time.sleep(500.0)

        now = time.time()
        print("The time is " + str(datetime.datetime.utcfromtimestamp(int(now))) + ".")
        make_graph("claims")
        make_graph("channels")
        aggregate_tips()

        try:
            publish_files()
        except:
            pass

