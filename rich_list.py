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
            GROUP BY support.id, support.support_amount, support.created_at) as t\
                GROUP BY publisher_id\
                ORDER BY total_lbc DESC) almost\
            INNER JOIN claim on claim.claim_id = almost.publisher_id"

request = requests.get("https://chainquery.lbry.com/api/sql?query=" + query)
the_dict = request.json()

k = 0
for row in the_dict["data"]:
    if row["publisher_id"] is not None:
        print(str(row["name"]) + "#" + str(row["publisher_id"]) + "," + str(row["total_lbc"]))
        k += 1
    if k >= 100:
        break

