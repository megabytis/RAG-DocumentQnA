# RAG-DocumentQnA

**RAG-DocumentQnA** is a Document Intelligence API built to ingest documents, index them, and answer user queries using context-aware retrieval (RAG) with traceable citations. The system restricts generation exclusively to retrieved evidence, effectively preventing LLM hallucinations.

## 🎯 System Objective

- **Ingest:** Extract text and metadata from documents (PDFs).
- **Index:** Create embeddings and store chunks in a vector database.
- **Retrieve:** Search the vector database for relevant information.
- **Generate:** Return context-backed answers containing source citations (doc_id, chunk_id, page).

---

## 🏗 System Architecture

The project strictly enforces a separation of concerns between business logic and AI/ML processing:

### 1. Backend Service (Node.js)

Located in `/server`, the backend service acts as the client-facing API layer.

- Handles user file uploads and request orchestration.
- Generates `doc_id` and tracks state.
- **Never** runs any AI inference or vector data logic directly.

### 2. AI Service (Python/FastAPI)

Located in `/ai-service`, the AI layer encapsulates all heavy lifting.

- **Ingestion Pipeline:** Parsing, chunking, and creating embeddings.
- **Retrieval Pipeline:** Vector similarity search (and future hybrid/BM25).
- **Generation Pipeline:** Interfacing with LLMs using strict prompts.
- **Never** handles HTTP business logic or user management.

---

## 🚀 API Workflows

### Flow 1: Document Ingestion

1. **Upload:** User hits `POST /upload` with a file to the Node.js API.
2. **Transfer:** Node.js generates a `doc_id` and forwards the request to the Python AI service.
3. **Process:** Python extracts text, splits into structural chunks with metadata, generates text embeddings, and stores them in the vector DB.
4. **Respond:** Indexing status is returned.

### Flow 2: Querying

1. **Query Request:** User sends a natural language query to the Node.js API via `POST /query`.
2. **Transfer:** Node.js forwards the query.
3. **Retrieval:** Python embeddings the query and performs a similarity search (top-k) targeting matching chunks.
4. **Generation:** Python sends context & query to the LLM.
5. **Respond:** Python returns the textual answer along with explicit `citations` (chunks, pages) back to the user.

---

## 💻 Local Setup (Step-by-Step)

To run this project locally, you will need to start both the Python AI Service and the Node.js Backend Service.

### Prerequisites

- Node.js (v18+)
- Python 3.9+
- An OpenAI API Key (or suitable alternative for `langchain_openai`)

### 1. Start the AI Service (Python)

The AI service handles vector operations, parsing, and LLM queries.

```bash
# Navigate to the ai-service folder
cd ai-service

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# (Optional) Set your API keys in the environment or a .env file
export OPENAI_API_KEY="your-api-key"

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

The AI Service will run at `http://localhost:8000`.

### 2. Start the Backend Service (Node.js)

The Node service handles incoming uploads and forwards requests.

```bash
# Open a new terminal and navigate to the server folder
cd server

# Install dependencies
npm install

# Start the development server
npm run dev
```

By default, the backend will communicate with the Python service (usually configured via `.env` in the root or server directory) and will start on port `5000`.

### 3. Testing with Postman

You can use Postman or cURL to interact with the system via the Node.js API.

**A. Uploading a Document**

- **Method:** `POST`
- **URL:** `http://localhost:5000/api/v1/file/upload`
- **Body:** `form-data`
  - Key: `file` (type: File)
  - Value: Select a PDF from your computer
- This will return an ingestion status and ideally a `doc_id`.

**B. Querying the Document**

- **Method:** `POST`
- **URL:** `http://localhost:5000/api/v1/query`
- **Body:** `raw` (JSON)
  ```json
  {
    "query": "What is the main topic of the uploaded document?",
    "doc_id": "<optional-doc-id>"
  }
  ```
- This will return a grounded LLM generated answer along with `citations`.

---

## 🛣 Execution Roadmap (Progressive Enhancement)

The system is designed to evolve gracefully from a naive RAG to a production-grade query engine:

- **Phase 1-2 (MVP):** Basic text extraction, static chunking, naive vector similarity search, simple API routing.
- **Phase 3 (Quality Fixes):** Recursive/structure-aware chunking, query cleaning and formatting.
- **Phase 4 (Advanced Retrieval):** Hybrid keyword/vector search combinations, result merging, and query re-ranking algorithms.
- **Phase 5 (Query Intelligence):** Query rewriting and multi-query expansions.
- **Phase 6+ (Evaluation):** Strict hallucination checks, coverage analysis, and measurement tools (Recall@k, MRR).

## 🛡️ Core Rules

The project adherence guidelines:

- **No LLM Guesswork:** Reject outputs without valid context.
- **Test Before Advancing:** Ensure working evaluation loops before adding complex components (e.g. LangGraph).
- **Strict Bounding:** Avoid merging AI functionality into typical backend code (Node), and avoid putting API controller logic into Python.
