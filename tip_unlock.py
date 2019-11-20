#!/usr/bin/env python

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

# Do non-channel claims (streams)
pages = daemon_command("stream list",
                       message="Getting number of pages...")["total_pages"]
k = 1
for page in range(1, pages+1):
    result = daemon_command("stream list --page={page}".format(page=page),
                                message="Getting page...")
    for item in result["items"]:
        print("Page {p}, item {k}, claim name {c}:\n    "\
                .format(p=page, k=k, c=item["name"]), end="")
        print("support abandon --claim_id={cid}".format(cid=item["claim_id"]),
                end="\n\n")
        k += 1


# Do channel claims
pages = daemon_command("channel list",
                       message="Getting number of pages...")["total_pages"]
k = 1
for page in range(1, pages+1):
    result = daemon_command("channel list --page={page}".format(page=page),
                                message="Getting page...")
    for item in result["items"]:
        print("Page {p}, item {k}, claim name {c}:\n    "\
                .format(p=page, k=k, c=item["name"]), end="")
        print("support abandon --claim_id={cid}".format(cid=item["claim_id"]),
                end="\n\n")
        k += 1

