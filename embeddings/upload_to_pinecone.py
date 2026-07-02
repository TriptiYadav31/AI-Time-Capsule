"""
One-time script: uploads all your chunks to Pinecone cloud vector database.
Run this ONCE from your local machine — after this, the cloud DB is ready
and Streamlit Cloud can query it directly.

USAGE:
    python embeddings/upload_to_pinecone.py
"""

import os
import json
import time
from pinecone import Pinecone, ServerlessSpec
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
INDEX_NAME = "time-capsule"
BATCH_SIZE = 100
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def get_embedder():
    return ONNXMiniLM_L6_V2()


def main():
    print("Loading chunks...")
    with open(os.path.join(PROCESSED_DIR, "chunks.json"), encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks")

    print("Connecting to Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create index if it doesn't exist
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing:
        print(f"Creating index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,  # all-MiniLM-L6-v2 outputs 384 dimensions
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        time.sleep(10)  # wait for index to be ready
    else:
        print(f"Index '{INDEX_NAME}' already exists, using it.")

    index = pc.Index(INDEX_NAME)
    embedder = get_embedder()

    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        embeddings = embedder(texts)

        vectors = [
            {
                "id": c["id"],
                "values": [float(x) for x in emb],
                "metadata": {
                    "date": c["date"],
                    "source": c["source"],
                    "year_month": c["date"][:7],
                    "text": c["text"],
                },
            }
            for c, emb in zip(batch, embeddings)
        ]

        index.upsert(vectors=vectors)
        print(f"  Uploaded {min(i + BATCH_SIZE, total)}/{total} chunks")
        time.sleep(0.5)

    print(f"\nDone! {total} chunks uploaded to Pinecone index '{INDEX_NAME}'")


if __name__ == "__main__":
    main()
