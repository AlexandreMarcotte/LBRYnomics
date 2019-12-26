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


# The queries used into
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



# Main loop
for i in range(1):

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

    # Calculate wait time
    duration = time.time() - now
    wait = 300.0 - duration
    if wait <= 0.0:
        wait = 1.0
    time.sleep(wait)

# Close connections
claims_db.close()
data_db.close()

