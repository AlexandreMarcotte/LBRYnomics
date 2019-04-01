from ira import *
import time

# Initialise one of these things
lbry = lbryRPC()

def get_data(channel_name, page_size=100):
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

            print("Processing tips from claim", end="", flush=True)

            for support in supports:
                try:
                    support_tx = lbry.lbry_call("transaction_show",
                                            {"txid": support["txid"]})
                    support_heights.append(support_tx[0]["height"])
                    support_amounts.append(float(support["amount"]))
                except:
                    time.sleep(3.0)
                    support_tx = lbry.lbry_call("transaction_show",
                                            {"txid": support["txid"]})
                    support_heights.append(support_tx[0]["height"])
                    support_amounts.append(float(support["amount"]))
                print(".", end="", flush=True)

            this_claim_data["claim_height"] = height
            this_claim_data["support_heights"] = support_heights
            this_claim_data["support_amounts"] = support_amounts
            this_claim_data["num_supports"] = len(support_heights)

            data.append(this_claim_data)
            print(".\nProcessed claim {num}.".format(num=len(data)))
            print(this_claim_data)
            print("\n", flush=True)

    return data


def write_flattened(data, filename="data.yaml"):
    """
    Input: a data list as output by get_data().
    Output: a YAML dataset in the current format.
    """
    # Extract times of claims, to get a start and time
    # (violating model assumptions slightly - end time should be current block
    # height, model should be modified so start time is first claim)
    times = []
    for claim in data:
        times.append(claim["claim_height"])

    f = open(filename, "w")
    f.write("---\n")
    f.write("t_start: " + str(min(times)) + "\n")
    t_end = max(times)

    # Get tip times and amounts
    times = []
    amounts = []
    for claim in data:
        times   = times + claim["support_heights"]
        amounts = amounts + claim["support_amounts"]
    t_end = max([t_end, max(times)])
    f.write("t_end: " + str(t_end) + "\n")

    f.write("times:\n")
    for time in times:
        f.write("    - " + str(time) + "\n")
    f.write("amounts:\n")
    for amount in amounts:
        f.write("    - " + str(amount) + "\n")

    f.close()


if __name__ == "__main__":
    data = get_data("@BrendonBrewer")
    write_flattened(data)

