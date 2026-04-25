import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

API = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"
URL = "https://api.groq.com/openai/v1"

client = OpenAI(
    api_key=API,
    base_url=URL,
)


def llm_judge(expected, actual):
    prompt = f"""judge if the actual answer matches with the expected answer.
    
    Expected: {expected}
    Actual: {actual}
    
    Reply with only: MATCH or NOT_MATCH
    
    No BS, No Fluff"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return "MATCH" in response.choices[0].message.content


queries = json.load(open("test_queries.json"))
results = []
retrieval_total = 0
retrieval_success = 0

for q in queries:
    payload = {
        "query": q["query"],
        "doc_ids": [q["doc_id"]] if q.get("doc_id") else []
    }
    
    try:
        res = requests.post("http://localhost:5000/api/v1/query", json=payload)
        res_data = res.json()
    except Exception as e:
        print(f"Failed to fetch for query: {q['query']}")
        continue

    # Answer accuracy evaluation
    if q["expected_answer"] is None:
        is_correct = "Cannot answer" in res_data.get("answer", "") or "NOT_FOUND" in res_data.get("answer", "")
    else:
        is_correct = llm_judge(expected=q["expected_answer"], actual=res_data.get("answer", ""))

    # Recall@K calculation
    retrieved_chunks = res_data.get("retrieved_chunks", [])
    recall_hit = False
    
    if q.get("relevant_chunk"):
        retrieval_total += 1
        if q.get("relevant_chunk_id") in retrieved_chunks:
            retrieval_success += 1
            recall_hit = True

    results.append(
        {
            "question": q["query"],
            "expected": q["expected_answer"],
            "got": res_data.get("answer", ""),
            "correct": is_correct,
            "recall_hit": recall_hit
        }
    )

accuracy = sum(r["correct"] for r in results) / len(results) if results else 0
recall_at_k = (retrieval_success / retrieval_total) if retrieval_total > 0 else 0

print(f"Accuracy: {accuracy*100:.2f}%")
print(f"Recall@K: {recall_at_k*100:.2f}%")
