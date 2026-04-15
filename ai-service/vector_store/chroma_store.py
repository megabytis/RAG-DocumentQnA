import chromadb
from chromadb.utils import embedding_functions


client = chromadb.PersistentClient(path="./data/chroma_db")

def store_embeddings(doc_id, chunks, embeddings):

    collection = client.create_collection(name=f"doc_{doc_id}")

    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[{"doc_id": doc_id, "chunk_idnex": i} for i in range(len(chunks))],
    )

    return {"status": "indexed", "doc_id": doc_id, "total_chunks": len(chunks)}

def search_doc(doc_id, query_embedding, n_results=5):
    collection = client.get_collection(f"doc_{doc_id}")
    results=collection.query(query_embeddings=[query_embedding],n_results=n_results)
    
    return results