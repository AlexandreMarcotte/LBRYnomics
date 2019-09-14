# Silly script to estimate ratio from logfile
directory = "/home/brewer/.local/share/lbry/lbrynet"

# Remove trailing slash if one was given
if directory[-1] == "/":
    directory = directory[0:-1]

suffices = ["", ".1", ".2", ".3", ".4", ".5"]
# Blob counts
up = 0
down = 0

for suffix in suffices:
    filename = directory + "/lbrynet.log" + suffix

    try:
        f = open(filename)
        lines = f.readlines()
        for line in lines:
            if "lbry.blob_exchange.server:105: sent" in line:
                up += 1
            if "lbry.blob_exchange.client:159: downloaded" in line:
                down += 1
        f.close()
    except:
        pass

print("Downloaded {down} blobs.".format(down=down))
print("Uploaded {up} blobs.".format(up=up))
print("Ratio = {ratio}".format(ratio=up/down))

