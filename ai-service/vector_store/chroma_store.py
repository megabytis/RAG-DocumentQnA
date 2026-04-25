import chromadb
from chromadb.utils import embedding_functions


client = chromadb.PersistentClient(path="./data/chroma_db")


from utils import normalize_chunks

def store_embeddings(doc_id, chunks, embeddings):

    collection = client.create_collection(name=f"doc_{doc_id}")
    chunks = normalize_chunks(chunks)

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = chunk["id"] if chunk["id"] else f"{doc_id}_{i}"
        chunk_text = chunk["text"]
        collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            metadatas=[{"doc_id": doc_id, "chunk_index": i, "text": chunk_text[:500]}],
        )

    return {"status": "indexed", "doc_id": doc_id, "total_chunks": len(chunks)}


def search_doc(doc_id, query_embedding, n_results=5):
    collection = client.get_collection(f"doc_{doc_id}")
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)

    return results
