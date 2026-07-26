import duckdb
con = duckdb.connect("analytics.duckdb")
print(con.execute("SELECT account_status, COUNT(*), AVG(balance) FROM customers GROUP BY account_status").fetchall())