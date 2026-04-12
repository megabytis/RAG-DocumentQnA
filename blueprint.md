# RAG-DocumentQnA — Execution Blueprint

## Core Rule

Build → hit friction → solve → continue.
No pre-learning. No detours.

---

# PHASE 0 — PROJECT SKELETON

### Task 0.1 — Initialize repo

- Create folders:

```
/src
  /ingestion
  /retrieval
  /generation
  /evaluation
  /api
/data
/scripts
/tests
```

### Task 0.2 — Decide stack

- Backend: Node.js (primary)
- Optional: Python microservice (only if needed for ML-heavy parts)

Decision constraint:

- If Node handles it → stay Node
- If blocked → isolate Python service (do NOT mix randomly)

---

# PHASE 1 — INGESTION PIPELINE

## Goal

Convert document → structured chunks + metadata

---

### Task 1.1 — File upload handling

- Accept: PDF (first only)
- Store locally (no cloud yet)

Think:

- What is the lifecycle of a document?
- How will you identify documents later? (doc_id)

---

### Task 1.2 — Text extraction

- Extract raw text from PDF

Think:

- Does extraction preserve structure?
- Are pages separable?

Output:

```
[
  { page: 1, text: "..." },
  { page: 2, text: "..." }
]
```

---

### Task 1.3 — Chunking (v1 naive)

- Fixed size chunks
- Add overlap

Think:

- Why overlap exists?
- What breaks if no overlap?

Output:

```
{
  chunk_id,
  doc_id,
  text,
  page
}
```

---

### Task 1.4 — Metadata design

Add:

- doc_id
- page
- chunk_index

Think:

- Future filtering?
- Multi-doc queries?

---

### Task 1.5 — Embeddings

- Convert chunk → vector

Think:

- Where does embedding live?
- Can you re-generate later?

---

### Task 1.6 — Storage

- Store:
  - vector
  - text
  - metadata

Think:

- Separation of concerns:
  - vector DB vs raw storage

---

# PHASE 2 — BASIC RETRIEVAL

## Goal

Query → relevant chunks

---

### Task 2.1 — Query embedding

- Convert user query → vector

---

### Task 2.2 — Similarity search

- Retrieve top-k chunks

Think:

- What is k?
- What happens if k too low / high?

---

### Task 2.3 — Response pipeline (v1)

- Pass chunks → LLM → answer

Think:

- Are you controlling output?
- Or letting model hallucinate?

---

### Task 2.4 — Minimal API

Endpoints:

- POST /upload
- POST /query

---

# PHASE 3 — FIX YOUR WEAK SYSTEM

## Goal

Remove obvious flaws

---

### Task 3.1 — Chunk quality upgrade

Replace naive chunking with:

- recursive / structure-aware

Think:

- Does chunk respect headings?
- Does it cut mid-sentence?

---

### Task 3.2 — Context formatting

Before sending to LLM:

- Clean
- Deduplicate
- Order logically

Think:

- Does order affect answer?

---

### Task 3.3 — Prompt control

- Force:
  - answer only from context
  - no guessing

Think:

- What happens when answer not found?

---

# PHASE 4 — RETRIEVAL UPGRADE

## Goal

Move beyond basic vector search

---

### Task 4.1 — Hybrid search

- Add BM25 / keyword search
- Combine with vector results

Think:

- When does keyword beat embeddings?

---

### Task 4.2 — Merge strategy

- Combine results
- Remove duplicates

---

### Task 4.3 — Re-ranking

- Score (query, chunk)
- Sort again

Think:

- Why initial retrieval is noisy?

---

# PHASE 5 — QUERY INTELLIGENCE

## Goal

Improve input before retrieval

---

### Task 5.1 — Query rewriting

- Rewrite unclear queries

Think:

- What is user actually asking?

---

### Task 5.2 — Multi-query expansion

- Generate multiple variations

Think:

- Different phrasings → different retrieval

---

### Task 5.3 — Fusion retrieval

- Run all queries
- Merge results

---

# PHASE 6 — ANSWER CONTROL

## Goal

Make output trustworthy

---

### Task 6.1 — Citation system

- Attach chunk_id to answers

Think:

- Can user verify answer?

---

### Task 6.2 — Confidence score

- Based on:
  - retrieval score
  - answer coverage

---

### Task 6.3 — Refusal mechanism

- If no good context → reject answer

Think:

- System honesty vs fake answers

---

# PHASE 7 — EVALUATION SYSTEM

## Goal

Make system measurable

---

### Task 7.1 — Dataset

- Create Q/A pairs from documents

---

### Task 7.2 — Metrics

Implement:

- Recall@K
- MRR

---

### Task 7.3 — Compare pipelines

Test:

- baseline vs hybrid vs rerank

Think:

- Which step actually improves results?

---

### Task 7.4 — Hallucination check

- Did answer use real context?

---

# PHASE 8 — LANGGRAPH (SIDE TRACK)

## Goal

Not required for core system

Use for:

- multi-step reasoning
- tool orchestration

DO NOT:

- over-engineer early

---

# EXECUTION RULES

1. One phase at a time
2. Ship working version before upgrading
3. No jumping ahead
4. If stuck:
   - isolate problem
   - solve only that

---

# FAILURE CONDITIONS

If you:

- keep adding features without evaluation
- copy tutorials
- avoid debugging retrieval quality

→ project becomes useless

---

# SUCCESS CRITERIA

System can:

- retrieve correct chunks consistently
- cite sources
- reject bad queries
- show measurable improvement across versions

---

# FINAL MENTAL MODEL

You are not building:
→ chatbot

You are building:
→ **information retrieval system with controlled reasoning**
