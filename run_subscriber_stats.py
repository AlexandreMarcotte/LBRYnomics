from fetch_data import *
import json
import time

# Needs an initial JSON file to bootstrap from

while True:
    f = open("subscriber_counts.json")
    t = json.load(f)["unix_time"]
    f.close()

    if time.time() - t >= 7*86400.0:
        subscriber_counts("") # <- Put auth token there as a string

    # Check about once an hour
    time.sleep(3600.0)

