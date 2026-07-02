import os
import json
import argparse
import chromadb

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "vector_db")


def get_collection():
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_or_create_collection("time_capsule")


def build(batch_size=2000):
    with open(os.path.join(PROCESSED_DIR, "chunks.json"), encoding="utf-8") as f:
        chunks = json.load(f)

    collection = get_collection()

    total = len(chunks)
    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[
                {"date": c["date"], "source": c["source"], "year_month": c["date"][:7]}
                for c in batch
            ],
        )
        print(f"  Stored chunks {i + 1}-{min(i + batch_size, total)} of {total}")

    print(f"Stored {total} chunks in {DB_DIR}")

def search(query, month_prefix, top_k=5, max_distance=1.5):
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"year_month": month_prefix},
    )

    matches = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        if dist <= max_distance:
            matches.append({"text": doc, "date": meta["date"], "source": meta["source"], "distance": dist})

    matches.sort(key=lambda m: m["distance"])
    return matches


def search_all(query, top_k=5, max_distance=1.5):
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=top_k)

    matches = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        if dist <= max_distance:
            matches.append({"text": doc, "date": meta["date"], "source": meta["source"], "distance": dist})

    return matches

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query")
    parser.add_argument("--month")
    args = parser.parse_args()

    if args.query:
        for r in search(args.query, args.month or ""):
            print(f"[{r['date']} | {r['source']}] {r['text']}")
    else:
        build()
