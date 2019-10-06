#!/usr/bin/env python
"""
Silly script to estimate recent LBRY ratio from logfiles
"""

# This should work on Linux. On other OSs you can try
# just setting the directory string yourself.
# You might need escape characters. E.g. on windows
# it could be something like
# directory = "C:/Program\ Files/..."
from os.path import expanduser
home = expanduser("~")
directory = home + "/.local/share/lbry/lbrynet"

# Remove trailing slash if one was given
if directory[-1] == "/":
    directory = directory[0:-1]

# Filename endings
suffices = [""] + ["." + str(i) for i in range(10)]

# Blob counts
up = 0
down = 0

# Flag that becomes true ones a file has been successfully opened
success = False
for suffix in suffices:
    filename = directory + "/lbrynet.log" + suffix

    try:
        f = open(filename)
        lines = f.readlines()
        for line in lines:
            if "lbry.blob_exchange.server:" and "sent" in line:
                up += 1
            if "lbry.blob_exchange.client:" and "downloaded" in line:
                down += 1
        f.close()

        success = True
    except:
        pass

print("Success = {success}.".format(success=success))
if success:
    print("Downloaded {down} blobs.".format(down=down))
    print("Uploaded {up} blobs.".format(up=up))
    print("Ratio = {ratio}.".format(ratio=up/down))

