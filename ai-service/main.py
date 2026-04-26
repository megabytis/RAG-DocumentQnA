import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
from loaders import load_file
from chunkers import chunk_text
from embedders import get_embedding
from vector_store import store_embeddings
from dotenv import load_dotenv
from retrieval import hybrid_search, rerank
from utils import normalize_chunks

load_dotenv()
from langchain_openai import ChatOpenAI
import json

API = os.getenv("GROQ_API_KEY")
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
URL = "https://api.groq.com/openai/v1"

llm = ChatOpenAI(
    model=MODEL,
    api_key=API,
    base_url=URL,
)


def call_llm(context, query):

    system_prompt = """Answer using ONLY the provided context.

    Rules:
    - Return ONLY the final answer.
    - Do NOT explain.
    - Do NOT add extra words.
    - Do NOT rephrase.

    If the answer is not explicitly present in the context:
    return exactly: NOT_FOUND
    """
    user_prompt = f"""CONTEXT:
    {context}

    QUESTION:
    {query}

    ANSWER:"""

    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return response.content


app = FastAPI()


class IngestRequest(BaseModel):
    doc_id: str
    file_path: str


# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),  # This keeps console output too
    ],
)


@app.post("/ingest")
async def ingest(request: IngestRequest):
    logging.info(f"Received: doc_id={request.doc_id}, file_path={request.file_path}")

    # checking wheather the file exists or not
    if not os.path.isfile(request.file_path):
        raise HTTPException(status_code=400, detail="file not found")

    # extracting file type
    file_type = os.path.splitext(request.file_path)[1]

    # reading contents from the file using the filepath and calling our loaders/ module
    result = load_file(file_path=request.file_path, file_type=file_type)
    # print(result)

    # chunking
    chunks = chunk_text(result, request.doc_id)
    chunks = normalize_chunks(chunks)

    # storing chunks
    chunks_dir = "chunks_store"
    if not os.path.exists(chunks_dir):
        os.makedirs(chunks_dir)

    with open(f"{chunks_dir}/{request.doc_id}.json", "w") as f:
        json.dump(chunks, f)

    # embeddings
    texts = [c["text"] for c in chunks]
    embeddings = get_embedding(texts)

    # storing embeddings
    store = store_embeddings(
        chunks=chunks, doc_id=request.doc_id, embeddings=embeddings
    )

    # response
    return {"status": "indexed", "doc_id": request.doc_id, "chunks": 0}


class QueryRequest(BaseModel):
    query: str
    doc_ids: list[str]


@app.post("/query")
async def query(request: QueryRequest):
    # logging.info(f"received query: {request.query} \n doc_id: {request.doc_id}")

    # query embedding
    query_embedding = get_embedding([request.query])[0]

    all_documents = []
    all_sources = []

    # searching in chroma DB
    for doc_id in request.doc_ids:
        results = hybrid_search(doc_id, request.query, query_embedding)
        all_documents.extend(results)
        all_sources.extend([doc_id] * len(results))

    # reranking
    final_chunks = rerank(query=request.query, chunks=all_documents)

    context = " ".join([c["text"] for c in final_chunks])
    retrieved_ids = [c["id"] for c in final_chunks]

    # sending chunks to LLM
    answer = call_llm(context, request.query)

    if "NOT_FOUND" in answer:
        return {"answer": "Cannot answer based on the documents", "found": False, "retrieved_chunks": retrieved_ids}

    return {"answer": answer, "doc_id": request.doc_ids, "sources": all_sources, "retrieved_chunks": retrieved_ids}
