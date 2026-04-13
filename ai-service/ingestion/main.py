import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging

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

    # response
    return {"status": "indexed", "doc_id": request.doc_id, "chunks": 0}
