# Trying to use chainquery
from pprint import pprint
import requests
import urllib.request

# Channel name
channel_name = "@BrendonBrewer"

# Get the channel's claim_id by doing a lbrynet resolve
from fetch_data import lbry
result = lbry.lbry_call("resolve", {"urls": [channel_name]})
claim_id = result[0][channel_name]["certificate"]["claim_id"]

# The SQL query to perform
query = "SELECT name from claim WHERE publisher_id = '" + claim_id + "';"

request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
the_dict = request.json()

if the_dict["success"]:
    pprint(the_dict)


