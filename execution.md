# RAG-DocumentQnA — Client Specification (Execution Contract)

## System Objective

Build a **Document Intelligence API** that:

- accepts documents
- indexes them
- answers queries using retrieved evidence
- returns citations

No UI required.

---

# SYSTEM ARCHITECTURE (MANDATORY SPLIT)

## Services

### 1. Backend Service (Node.js)

Responsibility:

- API layer
- auth (later)
- request orchestration
- file handling

### 2. AI Service (Python)

Responsibility:

- ingestion (parse, chunk, embed)
- retrieval (search, rerank)
- generation (LLM calls)

Strict rule:

- Node NEVER does AI logic
- Python NEVER handles HTTP business logic

---

# DIRECTORY CONTRACT

```id="m9x4tw"
RAG-DocumentQnA/
│
├── backend/        (Node.js)
│   ├── src/
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── services/
│   │   └── utils/
│
├── ai-service/     (Python)
│   ├── ingestion/
│   ├── retrieval/
│   ├── generation/
│   ├── db/
│   └── main.py
│
├── shared/
│   └── schemas/
│
├── data/
│   ├── raw_docs/
│   └── vector_store/
```

---

# COMMUNICATION CONTRACT (CRITICAL)

Use:

- HTTP (FastAPI in Python)

Endpoints exposed by AI service:

```id="c5z7yt"
POST /ingest
POST /query
```

Node acts as:
→ client to AI service

---

# END-TO-END FLOW

## FLOW 1 — DOCUMENT INGESTION

### Step 1 — Upload (Node)

- User sends file → Node
- Node:
  - generates doc_id
  - stores file in /data/raw_docs

---

### Step 2 — Call AI Service

Node → POST /ingest

Payload:

```id="3y3xqk"
{
  "doc_id": "...",
  "file_path": "..."
}
```

---

### Step 3 — AI Service Pipeline

Inside Python:

#### 3.1 Extract

- Read file
- Output: pages

#### 3.2 Chunk

- Create chunks
- Add metadata:
  - doc_id
  - page
  - chunk_id

#### 3.3 Embed

- Convert chunks → vectors

#### 3.4 Store

- Save in vector DB

Return:

```id="84n2i9"
{
  "status": "indexed",
  "chunks": N
}
```

---

### Step 4 — Node Response

- Return success to user

---

# FLOW 2 — QUERY

### Step 1 — Query Request (Node)

```id="kh8c7h"
POST /query
{
  "query": "...",
  "doc_id": "optional"
}
```

---

### Step 2 — Forward to AI Service

Node → POST /query

---

### Step 3 — AI SERVICE PIPELINE

#### 3.1 Query processing

- Embed query

(Optional later: rewrite / expand)

---

#### 3.2 Retrieval

- Vector search (top-k)
- Filter by doc_id if provided

---

#### 3.3 (Later upgrades)

- Hybrid search
- Re-ranking

---

#### 3.4 Context build

- Select top chunks
- format context

---

#### 3.5 Generation

- Send to LLM

Prompt must:

- restrict to context
- require citations

---

### Step 4 — Response format

```id="d3xk1m"
{
  "answer": "...",
  "citations": [
    { "chunk_id": "...", "page": 2 }
  ]
}
```

---

### Step 5 — Node returns response

---

# INTERNAL AI SERVICE DESIGN

## ingestion/

- loader.py
- chunker.py
- embedder.py

## retrieval/

- vector_search.py
- hybrid_search.py (later)
- reranker.py (later)

## generation/

- prompt_builder.py
- llm.py

## db/

- vector_store.py

---

# STATE DESIGN

Each chunk must be:

```id="m9p3zr"
{
  "chunk_id": "...",
  "doc_id": "...",
  "text": "...",
  "page": 1,
  "embedding": [...]
}
```

---

# VERSIONING STRATEGY

## v1 (must complete first)

- single doc
- vector search only
- basic answer

---

## v2

- multi-doc support
- metadata filtering

---

## v3

- hybrid search
- reranking

---

## v4

- query rewriting
- multi-query

---

## v5

- evaluation pipeline

---

# FAILURE CONDITIONS (STRICT)

Reject implementation if:

- Node contains embedding logic
- Python handles file upload API
- No doc_id tracking
- No metadata in chunks
- Direct LLM answering without retrieval

---

# THINKING MODEL

At every step:

- What is input?
- What is transformation?
- What is output?
- Where is state stored?

---

# FINAL EXPECTATION

System behaves like:

Input:
→ document

Output:
→ grounded answer with traceable evidence

Not acceptable:
→ “LLM guess”

Acceptable:
→ “retrieval-backed answer with citations”
