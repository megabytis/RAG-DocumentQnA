import json
from rank_bm25 import BM25Okapi
from vector_store import search_doc


def load_chunks(doc_id):
    with open(f"chunks_store/{doc_id}.json", "r") as f:
        return json.load(f)


def bm25_search(doc_id, query, top_k=3):
    chunks = load_chunks(doc_id)
    tokenized_chunks = [chunk.split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    tokenized_query = query.split()
    bm25_results = bm25.get_top_n(tokenized_query, chunks, n=top_k)
    return bm25_results


def hybrid_search(doc_id, query, embedded_query, top_k=3):
    bm25_results = bm25_search(doc_id, query, top_k=5)
    semantic_results = search_doc(
        doc_id=doc_id, query_embedding=embedded_query, n_results=5
    )

    combined = {}

    for i, chunk in enumerate(bm25_results):
        combined[chunk] = combined.get(chunk, 0) + (5 - i)

    for i, result in enumerate(semantic_results["documents"][0]):
        combined[result] = combined.get(result, 0) + (5 - i) * 2

    sorted_chunks = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    return [chunk_text for chunk_text, scpre in sorted_chunks[:top_k]]
