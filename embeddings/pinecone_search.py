"""
Search functions that query Pinecone instead of local ChromaDB.
Used by the Streamlit app and answer_question.py in production.
"""

import os
from pinecone import Pinecone
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
INDEX_NAME = "time-capsule"

_pc = None
_index = None
_embedder = None


def get_index():
    global _pc, _index
    if _index is None:
        _pc = Pinecone(api_key=PINECONE_API_KEY)
        _index = _pc.Index(INDEX_NAME)
    return _index


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = ONNXMiniLM_L6_V2()
    return _embedder


def search(query, month_prefix, top_k=5):
    index = get_index()
    embedder = get_embedder()
    query_embedding = [float(x) for x in embedder([query])[0]]

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter={"year_month": {"$eq": month_prefix}},
        include_metadata=True,
    )

    matches = []
    for match in results["matches"]:
        matches.append({
            "text": match["metadata"]["text"],
            "date": match["metadata"]["date"],
            "source": match["metadata"]["source"],
            "distance": round(1 - match["score"], 3),
        })

    return matches


def search_all(query, top_k=5):
    index = get_index()
    embedder = get_embedder()
    query_embedding = [float(x) for x in embedder([query])[0]]

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    matches = []
    for match in results["matches"]:
        matches.append({
            "text": match["metadata"]["text"],
            "date": match["metadata"]["date"],
            "source": match["metadata"]["source"],
            "distance": round(1 - match["score"], 3),
        })

    return matches
