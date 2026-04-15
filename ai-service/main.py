import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
from loaders import load_file
from chunkers import chunk_text
from embedders import get_embedding
from vector_store import store_embeddings

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
    chunks = chunk_text(result)
    # for i, chunk in enumerate(chunks[:2]):
    #     print(f"Chunk {i}: {chunk[:100]}...")

    # embeddings
    embeddings = get_embedding(chunks)

    # storing embeddings
    store = store_embeddings(
        chunks=chunks, doc_id=request.doc_id, embeddings=embeddings
    )

    # response
    return {"status": "indexed", "doc_id": request.doc_id, "chunks": 0}
