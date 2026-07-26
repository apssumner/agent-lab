import sqlite3

conn = sqlite3.connect("customers.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    account_status TEXT NOT NULL,
    balance REAL NOT NULL
)
""")

customers = [
    ("C001", "Alice Dupont", "active", 4230.50),
    ("C002", "Ben Okafor", "dormant", 12.00),
    ("C003", "Chidi Nwosu", "active", 980.75),
]

cursor.executemany(
    "INSERT OR REPLACE INTO customers (customer_id, name, account_status, balance) VALUES (?, ?, ?, ?)",
    customers
)

conn.commit()
conn.close()
print("customers.db created and populated.")