import sqlite3
import duckdb 
import chromadb
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("customer-server")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
policy_collection = chroma_client.get_collection("bank_policies")

@mcp.tool()
def lookup_customer(customer_id: str) -> dict:
    """Look up a bank customer's record by their customer ID. Returns name, account status, and balance."""
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, account_status, balance FROM customers WHERE customer_id = ?",
        (customer_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {"error": f"No customer found with ID {customer_id}"}

    name, account_status, balance = row
    return {"name": name, "account_status": account_status, "balance": balance}

@mcp.tool()
def customer_balance_summary() -> dict:
    """Get aggregate balance statistics grouped by account status (e.g. active, dormant) across all customers."""
    con = duckdb.connect("analytics.duckdb")
    rows = con.execute(
        "SELECT account_status, COUNT(*), AVG(balance) FROM customers GROUP BY account_status"
    ).fetchall()
    con.close()

    summary = {}
    for status, count, avg_balance in rows:
        summary[status] = {"count": count, "average_balance": round(avg_balance, 2)}

    return summary

@mcp.tool()
def search_policies(question: str) -> dict:
    """Search the bank's policy documents semantically to answer a question about rules, procedures, or compliance requirements. Returns the most relevant policy text(s)."""
    # query the collection for the most relevant documents
    results = policy_collection.query(query_texts=[question], n_results=2)

    # results may contain a "documents" key with a list of lists (one list per query)
    documents = results.get("documents", [])
    matches = documents[0] if documents else []  # type: ignore

    if not matches:
        return {"results": "No relevant policies found."}

    return {"relevant_policies": matches}

if __name__ == "__main__":
    mcp.run()