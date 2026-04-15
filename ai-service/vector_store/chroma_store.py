import chromadb
from chromadb.utils import embedding_functions


def store_embeddings(doc_id, chunks, embeddings):
    client = chromadb.PersistentClient(path="./data/chroma_db")

    collection = client.create_collection(name=f"doc_{doc_id}")

    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[{"doc_id": doc_id, "chunk_idnex": i} for i in range(len(chunks))],
    )

    return {"status": "indexed", "doc_id": doc_id, "total_chunks": len(chunks)}
