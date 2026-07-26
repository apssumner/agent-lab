import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

# Delete and recreate the collection each time we run this, so re-runs don't duplicate data
try:
    client.delete_collection("bank_policies")
except Exception:
    pass

collection = client.create_collection("bank_policies")

policies = [
    {
        "id": "policy_1",
        "text": "Customers with dormant accounts for over 12 months must be contacted before any funds can be withdrawn, to verify identity and reduce fraud risk.",
    },
    {
        "id": "policy_2",
        "text": "Any single transaction exceeding 10,000 GBP must be flagged for manual review under anti-money-laundering procedures.",
    },
    {
        "id": "policy_3",
        "text": "New customer accounts require two forms of identification before the account can be marked as fully verified and unrestricted.",
    },
    {
        "id": "policy_4",
        "text": "Overdraft fees are waived for customers who are enrolled in the financial hardship support programme.",
    },
    {
        "id": "policy_5",
        "text": "Joint accounts require authorization from both named account holders before a standing order can be cancelled.",
    },
]

collection.add(
    ids=[p["id"] for p in policies],
    documents=[p["text"] for p in policies],
)

print(f"Loaded {len(policies)} policy documents into Chroma.")