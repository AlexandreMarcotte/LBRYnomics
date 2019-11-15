#!/usr/bin/env python
"""
Silly script to boost a claim once every six hours
"""
import json
import subprocess
import time

# Full path to the lbrynet binary
lbrynet_bin = "/opt/LBRY/resources/static/daemon/lbrynet"

def daemon_command(command, message="Calling lbrynet daemon..."):
    """
    Run a daemon command and return its output.
    """
    print(message, end="", flush=True)
    command = lbrynet_bin + " " + command
    parts = command.split(" ")
    output = subprocess.run(parts, capture_output=True)
    print("done.")
    return json.loads(output.stdout)

# Get some input
url = input("Enter LBRY URL to boost: ")

# Resolve it to get claim_id
result = daemon_command("resolve " + url, "Resolving URL to get claim_id...")

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

# Any initial delay?
delay = float(input("Delay before first support, in hours (e.g., 0, 1, 2, 3, ...): "))*3600.0

# Check available balance
balance = float(daemon_command("account balance",
                               message="Checking available balance...")["available"])
if amount*reps > balance:
    print("You don't have enough LBC to do this!")
    exit()

# Now do the supports
time.sleep(delay)
for i in range(reps):
    daemon_command("support create --claim_id=" + claim_id \
                        + " --amount=" + str(float(amount)),
                   message="Depositing support #{k}...".format(k=i+1))

    if i != reps-1:
        time.sleep(6*3600) # Wait six hours

