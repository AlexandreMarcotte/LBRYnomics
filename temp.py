from ira import *

# Initialise one of these things
lbry = lbryRPC()

def get_data(channel_name, page_size=10):
    """
    Get all the data from a given channel and return it in a nice
    format (list of dicts).
    """

    # Get number of claims and number of pages
    result = lbry.claim_list_by_channel(channel_name, page=0)
    num_claims = result[0][channel_name]["claims_in_channel"]
    num_pages = 1 + num_claims // page_size

    # Loop over the claims, pack the required data into a list
    data = []
    for page in range(1, num_pages+1):
        result = lbry.claim_list_by_channel(channel_name,
                                            page=page, page_size=page_size)

        # Go where the important stuff is
        claims = result[0][channel_name]["claims_in_channel"]

        for claim in claims:

            # Get the block height of the transaction
            height = claim["height"]

            # Get the supports
            supports = claim["supports"]

            # Get the heights and amounts of the supports
            this_claim_data = {}
            support_heights = []
            support_amounts = []

            for support in supports:
                try:
                    support_tx = lbry.lbry_call("transaction_show",
                                            {"txid": support["txid"]})
                    support_heights.append(support_tx[0]["height"])
                    support_amounts.append(float(support["amount"]))
                except:
                    print("Error encountered. Trying again in 5 seconds.")
                    import time
                    time.sleep(5.0)

                    support_tx = lbry.lbry_call("transaction_show",
                                            {"txid": support["txid"]})
                    support_heights.append(support_tx[0]["height"])
                    support_amounts.append(float(support["amount"]))

            this_claim_data["claim_height"] = height
            this_claim_data["support_heights"] = support_heights
            this_claim_data["support_amounts"] = support_amounts
            this_claim_data["num_supports"] = len(support_heights)

            data.append(this_claim_data)
            print("Processed claim {num}.".format(num=len(data)))
            print(this_claim_data)
            print("\n\n\n\n", flush=True)

    return data



def write_flattened(data, filename="data.yaml"):
    """
    Input: a data list as output by get_data().
    Output: a YAML dataset in the current format.
    """
    f = open(filename, "w")
    f.write("---")
    f.close()


if __name__ == "__main__":
    x = get_data("@TheCryptoLark")
    write_flattened(data)

