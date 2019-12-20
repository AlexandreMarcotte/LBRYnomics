from fetch_data import *
import json
import numpy
import time

# Needs an initial JSON file to bootstrap from

hour = 3600.0
day = 24*hour
week = 7*day


f = open("subscriber_counts.json")
t = json.load(f)["unix_time"]
f.close()


while True:
    gap = time.time() - t

    msg = "{d} days until next update.".format(d=(week - gap)/day)
    print(msg, end="\r", flush=True)
    time.sleep(1.0 - time.time()%1)

    if gap >= week:
        subscriber_counts("") # <- Put auth token there as a string

        f = open("subscriber_counts.json")
        t = json.load(f)["unix_time"]
        f.close()

