import json
from rank_bm25 import BM25Okapi
from vector_store import search_doc
from utils import normalize_chunks


def load_chunks(doc_id):
    with open(f"chunks_store/{doc_id}.json", "r") as f:
        chunks = json.load(f)
        return normalize_chunks(chunks)


def bm25_search(chunks, query, top_k=15):
    tokenized_chunks = [chunk["text"].split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    tokenized_query = query.split()
    bm25_results = bm25.get_top_n(tokenized_query, chunks, n=top_k)
    return bm25_results


def hybrid_search(doc_id, query, embedded_query, top_k=15):
    chunks = load_chunks(doc_id)

    for idx, c in enumerate(chunks):
        c["_index"] = idx

    bm25_results = bm25_search(chunks, query, top_k=top_k)
    semantic_results = search_doc(
        doc_id=doc_id, query_embedding=embedded_query, n_results=top_k
    )

    combined = {}

    for i, chunk in enumerate(bm25_results):
        idx = chunk["_index"]
        combined[idx] = combined.get(idx, 0) + (top_k - i)

    semantic_metadatas = semantic_results.get("metadatas", [[]])[0]
    for i, metadata in enumerate(semantic_metadatas):
        idx = metadata.get("chunk_index")
        if idx is not None and idx < len(chunks):
            combined[idx] = combined.get(idx, 0) + (top_k - i) * 2

    sorted_idxs = sorted(combined.items(), key=lambda x: x[1], reverse=True)

    top_chunks = []
    for idx, score in sorted_idxs[:top_k]:
        chunk = chunks[idx]
        result_chunk = {k: v for k, v in chunk.items() if k != "_index"}
        top_chunks.append(result_chunk)

    return top_chunks
