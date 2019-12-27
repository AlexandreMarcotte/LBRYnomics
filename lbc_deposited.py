"""
Measure LBC deposited in claims and supports
"""
import sqlite3
import time

# Create connection to claims.db and data db
claims_db = sqlite3.connect("/home/brewer/local/lbry-sdk/lbry/lbryum_data/claims.db")
claims_db_cursor = claims_db.cursor()

data_db = sqlite3.connect("data.db")
data_db_cursor = data_db.cursor()

# Create tables in data.db
data_db_cursor.execute("PRAGMA journal_mode=WAL;")
data_db_cursor.execute("""
CREATE TABLE IF NOT EXISTS `measurements` (
	`id`	INTEGER NOT NULL,
	`time`	REAL NOT NULL,
	`deposits`	REAL NOT NULL,
	`supports`	REAL NOT NULL,
	`num_claims`	INTEGER NOT NULL,
	`num_supports`	INTEGER NOT NULL,
	PRIMARY KEY(`id`)
);""")


# The queries used
queries = ["""
SELECT SUM(amount)/1E8 AS deposits,
       SUM(support_amount)/1E8 AS supports,
       COUNT(*) AS num_claims
FROM claim;
""", """
SELECT COUNT(*) AS num_supports
FROM support;
""",
"""
INSERT INTO measurements (time, deposits, supports, num_claims, num_supports)
        VALUES(?, ?, ?, ?, ?);
"""]


def create_plot():
    q = "SELECT time, deposits, supports FROM measurements;"
    time = []
    deposits = []
    supports = []
    for row in data_db_cursor.execute(q):
        t, d, s = row
        time.append(t)
        deposits.append(d)
        supports.append(s)

    import matplotlib.pyplot as plt
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    plt.plot(time, deposits)
    plt.title("LBC in Deposits")
    plt.xlabel("Time")
    plt.ylabel("LBC")
    plt.subplot(1, 2, 2)
    plt.plot(time, supports)
    plt.ylabel("LBC")
    plt.title("LBC in Supports")

    plt.savefig("lbc_deposited.svg")
    plt.close("all")

# Main loop
while True:

    print("Making measurements...", end="", flush=True)

    # Get current unix time
    now = time.time()

    # Row of data to add
    measurement = [now]
    for row in claims_db_cursor.execute(queries[0]):
        measurement += list(row)
    for row in claims_db_cursor.execute(queries[1]):
        measurement += list(row)

    data_db_cursor.execute(queries[2], tuple(measurement))
    data_db_cursor.execute("COMMIT;")
    print("done.")

    # Create plot
    print("Creating plot...", end="", flush=True)
    create_plot()
    print("done.")

    # Calculate wait time
    duration = time.time() - now
    wait = 300.0 - duration
    if wait <= 0.0:
        wait = 1.0
    print("Waiting...", end="", flush=True)
    time.sleep(wait)
    print("done.")

# Close connections
claims_db.close()
data_db.close()

