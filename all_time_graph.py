"""
Get the timestamps of all claims and plot the cumulative number vs. time!
"""

import datetime
import json
import matplotlib.pyplot as plt
import math
import numpy as np
import os
import requests
import sqlite3
import subprocess
import time


# Full path to the lbrynet binary
lbrynet_bin = "/opt/LBRY/resources/static/daemon/lbrynet"

def daemon_command(command, message="Calling lbrynet daemon..."):
    """
    Run a daemon command and return its output.
    """
    command = lbrynet_bin + " " + command
    parts = command.split(" ")
    output = subprocess.run(parts, capture_output=True)
    return json.loads(output.stdout)




def make_graph(mode, show=True):
    """
    mode must be "claims" or "channels"
    """
    if mode != "claims" and mode != "channels":
        return

    plt.close("all")

    # Open the DB
    db_file = "/home/brewer/local/lbry-sdk/lbry/lbryum_data/claims.db"
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
    f.write(json.dumps(my_dict, indent=2))
    f.close()

    # Count new claims this UTC day
    count_today = np.sum(times > 86400.0*int(now/86400.0))
    if mode == "claims":
        string = "publications"
    else:
        string = "channels"
    print("{K} {mode}, {n} from today so far (UTC). ".format(K=len(times), mode=string, n=count_today), end="", flush=True)



    # Plotting stuff
    plt.rcParams["font.family"] = "Liberation Sans"
    plt.rcParams["font.size"] = 14
    plt.style.use("dark_background")
    plt.rcParams["axes.facecolor"] = "#3c3d3c"
    plt.rcParams["savefig.facecolor"] = "#3c3d3c"

    plt.figure(figsize=(15, 11))
    plt.subplot(2, 1, 1)
    times_in_days = (times - 1483228800)/86400.0
    days = times_in_days.astype("int64")
    plt.plot(times_in_days,
                np.arange(len(times)), "w-", linewidth=1.5)
    plt.ylabel("Cumulative number of {mode}".format(mode=string))
    plt.title("Total number of {mode} = {n}.".format(n=len(times), mode=string))
    plt.xlim([0.0, days.max() + 1])
    plt.ylim(bottom=-100)
    plt.gca().tick_params(labelright=True)

    # Add vertical lines for new years (approximately)
    new_years = np.arange(0, 5)*365.2425
    for year in new_years:
        plt.axvline(year, color="r", alpha=0.8, linestyle="--")

    # Add text about years
    year_names = [2017, 2018, 2019]
    for i in range(len(year_names)):
        year = new_years[i]
        plt.text(year+5.0, 0.95*plt.gca().get_ylim()[1],
                    "{text} begins".format(text=year_names[i]),
                    fontsize=10)

    # Add line and text about MH's video
    plt.axvline(890.0, linestyle="dotted", linewidth=2, color="g")
    plt.text(890.0, 0.2*plt.gca().get_ylim()[1],
            "@MH video\n\'Why I Left YouTube\'\ngoes viral",
            fontsize=10)

    plt.subplot(2, 1, 2)
    bin_width = 1.0

    # Bin edges including right edge of last bin
    bins = np.arange(0, np.max(days)+2) - 0.5*bin_width
    color = "#6b95ef"
    counts = plt.hist(days, bins, alpha=0.9, color=color, label="Raw",
                        width=bin_width, align="mid")[0]

    # Compute 10-day moving average
    moving_average = np.zeros(len(bins)-1)
    for i in range(len(moving_average)):
        subset = counts[0:(i+1)]
        if len(subset) >= 10:
            subset = subset[-10:]
        moving_average[i] = np.mean(subset)
    plt.plot(bins[0:-2] + 0.5*bin_width, moving_average[0:-1], "w-",
                label="10-day moving average", linewidth=1.5)

    plt.xlim([0.0, days.max() + 1])
    plt.xlabel("Time (days since 2017-01-01)")
    plt.ylabel("New {mode} added each day".format(mode=string))
    subset = counts[-31:-1]
    plt.title("Recent average rate (last 30 days) = {n} {mode} per day.".\
                format(n=int(np.sum(time.time() - times <= 30.0*86400.0)/30.0),
                       mode=string))

    plt.gca().tick_params(labelright=True)
    # Year lines
    for year in new_years:
        plt.axvline(year, color="r", alpha=0.8, linestyle="--")

    # MH line
    plt.axvline(890.0, linestyle="dotted", linewidth=2, color="g")


    #        plt.gca().set_yticks([1.0, 10.0, 100.0, 1000.0, 10000.0])
    #        plt.gca().set_yticklabels(["1", "10", "100", "1000", "10000"])
    plt.legend()

    plt.savefig("{mode}.svg".format(mode=mode), bbox_inches="tight")
    plt.savefig("{mode}.png".format(mode=mode), bbox_inches="tight", dpi=70)
    print("Figure saved to {mode}.svg and {mode}.png.".format(mode=mode))
    if show:
        plt.show()

def aggregate_tips():
    """
    Calculate tips over past X amount of time and write JSON output
    """

    # The SQL query to perform
    now = time.time()
    print("Computing tip stats...", end="", flush=True)
    labels = ["all_time", "30_days", "7_days", "24_hours", "1_hour"]
    windows = [None, 30*86400.0, 7*86400.0, 1*86400.0, 3600.0]
    result = {}
    result["unix_time"] = now
    result["human_time_utc"] =\
                    str(datetime.datetime.utcfromtimestamp(int(now))) + " UTC"
    block = daemon_command("status")["wallet"]["blocks"]

    # Open the DB
    db_file = "/home/brewer/local/lbry-sdk/lbry/lbryum_data/claims.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    conn.create_function("log", 1, math.log)
    conn.create_function("exp", 1, math.exp)

    for i in range(len(labels)):

        # Count and aggregate tips and supports for the time window
        query = \
                """
                SELECT
                    COUNT(amount) num,
                    exp(AVG(log(amount))) size,
                    MAX(amount) max
                FROM
                    support
                """

        if i > 0:
            query += \
                """ WHERE
                    height >= {cutoff};
                """.format(cutoff=block - windows[i]/(2.5*60))

        for row in c.execute(query):
            biggest = row[2]
            result["num_{label}".format(label=labels[i])] = row[0]
            result["typical_{label}".format(label=labels[i])] = row[1]/1.0E8
            result["biggest_{label}".format(label=labels[i])] = row[2]/1.0E8
            break

        # Get claim name and ID for max
        query = \
                """
                SELECT
                    claim_name, claim_id
                FROM
                    claim INNER JOIN support ON claim.claim_hash = support.claim_hash
                WHERE
                    support.amount = {amount}
                """.format(amount=biggest)

        if i > 0:
            query += \
                """ AND
                    support.height >= {cutoff};
                """.format(cutoff=block - windows[i]/(2.5*60))

        for row in c.execute(query):
            claim_name, claim_id = row[0:2]

        result["tv_url_{label}".format(label=labels[i])] = "https://lbry.tv/" \
                + claim_name + ":" + claim_id

        # Get claim name and ID for max
        query = \
                """
                SELECT
                    COUNT(claim_id)
                FROM
                    claim INNER JOIN tag ON claim.claim_hash = tag.claim_hash
                    INNER JOIN support ON support.claim_hash = claim.claim_hash
                WHERE ((tag.tag = "mature" OR tag.tag = "nsfw" OR
                       tag.tag = "porn" OR tag.tag = "xxx")
                      AND support.amount = {amount})
                """.format(amount=biggest)

        if i > 0:
            query += \
                """ AND
                    support.height >= {cutoff};
                """.format(cutoff=block - windows[i]/(2.5*60))

        for row in c.execute(query):
            result["is_nsfw_{label}".format(label=labels[i])] = row[0] != 0
            break

    f = open("supports_and_tips.json", "w")
    f.write(json.dumps(result, indent=2))
    f.close()
    conn.close()
    print("done. ", flush=True, end="")


def publish_files():
    """
    Publish files to somewhere on the internet.
    """
    print("Publishing files to the internet...", end="", flush=True)
    import subprocess
    try:
        subprocess.run("./upload.sh", timeout=120.0)
        print("done.\n")
    except:
        print("failed.\n")


if __name__ == "__main__":

    # Do it manually once then enter the infinite loop
    start = time.time()
    print("The time is " + str(datetime.datetime.utcfromtimestamp(int(start))) + " UTC.")
    make_graph("claims")
    make_graph("channels")
    try:
        aggregate_tips()
    except:
        pass

    try:
        publish_files()
    except:
        pass
    finish = time.time()
    duration = finish - start


    while True:
        print("", flush=True)
        time.sleep(300.0 - duration)

        start = time.time()
        print("The time is " + str(datetime.datetime.utcfromtimestamp(int(start))) + " UTC.")
        make_graph("claims", show=False)
        make_graph("channels", show=False)
        try:
            aggregate_tips()
        except:
            pass

        try:
            publish_files()
        except:
            pass

        finish = time.time()
        duration = finish - start

