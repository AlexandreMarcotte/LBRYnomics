import json
import matplotlib.pyplot as plt
import numpy as np
import subprocess

# Full path to the lbrynet binary
lbrynet_bin = "/opt/LBRY/resources/static/daemon/lbrynet"

def daemon_command(command):
    """
    Run a daemon command and return its output.
    """
    command = lbrynet_bin + " " + command
    parts = command.split(" ")
    output = subprocess.run(parts, capture_output=True)
    return json.loads(output.stdout)


class TransactionHistory:
    """
    Represent a transaction history.
    """
    def __init__(self):
        """
        Initialises timestamps empty.
        """
        self.timestamps = []

    def add_transaction(self, tx):
        self.timestamps.append(tx["timestamp"])


    def display(self):
        plt.hist(self.timestamps, 100)
        plt.show()


if __name__ == "__main__":

    # Get number of pages
    num_pages = daemon_command("transaction list")["total_pages"]
    print("You have {num_pages} pages of transactions to process."\
                .format(num_pages=num_pages), end="\n\n")

    # Create an object representing the tx history
    history = TransactionHistory()

    # Process pages
    for i in range(num_pages):
        page = i+1
        transactions = daemon_command("transaction list --page={p}"\
                                            .format(p=page))["items"]
        for tx in transactions:
            history.add_transaction(tx)

        print("Done page {p}.".format(p=page))

    history.display()

