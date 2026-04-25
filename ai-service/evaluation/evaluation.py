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

for q in queries:
    res = requests.post("http://localhost:5000/api/v1/query", json=q)
    res_data = res.json()

    is_correct = llm_judge(expected=q["expected_answer"], actual=res_data["answer"])

    results.append(
        {
            "question": q["query"],
            "expected": q["expected_answer"],
            "got": res_data["answer"],
            "correct": is_correct,
        }
    )


accuracy = sum(r["correct"] for r in results) / len(results)
print(f"Accuracy: {accuracy*100}%")
