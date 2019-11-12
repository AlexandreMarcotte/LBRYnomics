#!/usr/bin/env python
"""
Silly script to boost a claim once every six hours
"""
import json
import subprocess
import time

# Full path to the lbrynet binary
lbrynet_bin = "/opt/LBRY/resources/static/daemon/lbrynet"

def daemon_command(command):
    """
    Run a daemon command and return its output.
    """
    print("Calling lbrynet daemon...", end="", flush=True)
    command = lbrynet_bin + " " + command
    parts = command.split(" ")
    output = subprocess.run(parts, capture_output=True)
    print("done.")
    return json.loads(output.stdout)

# Get some input
url = input("Enter LBRY URL to boost: ")

# Resolve it to get claim_id
result = daemon_command("resolve " + url)

# Get claim_id
try:
    claim_id = result[url]["claim_id"]
except:
    print("Error resolving claim.")
    exit()

# Amount and repetitions
amount = float(input("LBC amount of support: "))

# How many times?
reps = int(input("Number of repetitions: "))

# Check available balance
balance = float(daemon_command("account balance")["available"])
if amount*reps > balance:
    print("You don't have enough LBC to do this!")
    exit()

# Now do the supports
for i in range(reps):
    daemon_command("support create --claim_id=" + claim_id \
                        + " --amount=" + str(float(amount)))
    time.sleep(6*3600) # Wait six hours


