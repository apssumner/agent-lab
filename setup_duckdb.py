import duckdb

con = duckdb.connect("analytics.duckdb")

con.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR,
    name VARCHAR,
    account_status VARCHAR,
    balance DOUBLE
)
""")

con.execute("DELETE FROM customers")  # avoid duplicate rows if rerun

con.executemany(
    "INSERT INTO customers VALUES (?, ?, ?, ?)",
    [
        ("C001", "Alice Dupont", "active", 4230.50),
        ("C002", "Ben Okafor", "dormant", 12.00),
        ("C003", "Chidi Nwosu", "active", 980.75),
        ("C004", "Diane Martin", "active", 15230.00),
        ("C005", "Emeka Obi", "dormant", 0.00),
    ]
)

con.close()
print("analytics.duckdb created and populated.")