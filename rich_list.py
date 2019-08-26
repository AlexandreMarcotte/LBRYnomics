import numpy as np
import requests

# The SQL query to perform
# NB: The use of the claim_address and the address_list from the output
# table is to try to only capture tips (not other supports). This also
# will not capture tips sent to the channel itself.
query = "SELECT name, almost.* FROM\
            (SELECT t.publisher_id, SUM(t.amount) total_lbc from (SELECT name, publisher_id, support.support_amount amount\
            FROM claim\
            INNER JOIN support ON support.supported_claim_id = claim.claim_id\
            INNER JOIN transaction ON support.transaction_hash_id = transaction.hash\
            INNER JOIN output ON transaction.hash = output.transaction_hash \
              AND output.address_list LIKE CONCAT('%25', claim_address, '%25')\
              AND transaction.hash <> 'e867afabfa52bea6d5af84e65865dd5d0382c340646f1578192768033be48924'\
            GROUP BY support.id, support.support_amount, support.created_at) as t\
                GROUP BY publisher_id\
                ORDER BY total_lbc DESC) almost\
            INNER JOIN claim on claim.claim_id = almost.publisher_id"

request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
the_dict = request.json()

f = open("richlist.csv", "w")
f.write("rank,vanity_name,claim_id,total_lbc_tips\n")
k = 0
for row in the_dict["data"]:
    if row["publisher_id"] is not None:
        k += 1
        f.write(str(k) + "," + str(row["name"]) + "," +\
                str(row["publisher_id"]) + "," +\
                str(row["total_lbc"]) + "\n")

    if k >= 1000:
        break
f.close()

# Compare with previous version
import numpy as np
import pandas as pd
x = pd.read_csv("richlist.csv")
y = pd.read_csv("/home/brewer/Downloads/LBRY/richlist.csv")

fresh = {"rank": [], "vanity_name": [], "claim_id": [], "total_lbc_tips": [],\
         "change": [], "rank_change": []}
for i in range(x.shape[0]):
    claim_id = x["claim_id"][i]

    # Look it up in y
    row = np.nonzero(y["claim_id"].to_numpy() == claim_id)[0]

    # Copy over into dict
    fresh["rank"].append(x["rank"][i])
    fresh["vanity_name"].append(x["vanity_name"][i])
    fresh["claim_id"].append(claim_id)
    fresh["total_lbc_tips"].append(x["total_lbc_tips"][i])

    if len(row) == 1:
        fresh["change"].append(float(fresh["total_lbc_tips"][-1] - y["total_lbc_tips"][row]))
        fresh["rank_change"].append(int(y["rank"][row] - fresh["rank"][-1]))
    else:
        fresh["change"].append(np.nan)
        fresh["rank_change"].append(np.nan)
fresh = pd.DataFrame(fresh)
fresh["total_lbc_tips"] = np.round(fresh["total_lbc_tips"], 2)
fresh["change"] = np.round(fresh["change"], 2)
fresh.to_csv("richlist.csv", index=False)


