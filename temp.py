from ira import *

# Initialise one of these things
lbry = lbryRPC()

# Channel name and page size
channel = "@BrendonBrewer"
page_size = 100 # There better be less claims than this, or I'll need more pages

# Get a lbry call
result = lbry.claim_list_by_channel(channel, page=1, page_size=page_size)

# Go where the important stuff is
claims = result[0][channel]["claims_in_channel"]

# Loop over the claims, get supports
for claim in claims:
    support = claim["supports"]
    if len(support) > 0:
        print(support)

