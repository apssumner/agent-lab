import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("bank_policies")

results = collection.query(
    query_texts=["What happens if I try to move a large amount of money?"],
    n_results=2,
)

for doc, distance in zip(results["documents"][0], results["distances"][0]): # type: ignore
    print(f"Distance: {distance:.4f} -- {doc}")