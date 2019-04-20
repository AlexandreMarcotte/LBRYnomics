# Trying to use chainquery instead of ira
from pprint import pprint
import requests
import urllib.request

# The SQL query to perform
query = "SELECT * from claim WHERE name=\"lbry\""

request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
json = request.json()

pprint(json)

