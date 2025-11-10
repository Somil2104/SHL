import os
import json
import pickle
import faiss
import numpy as np
from openai import OpenAI
import re

# ---------------- CONFIG ----------------
INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/faiss_index/index.faiss")
META_PATH = os.getenv("META_PATH", "data/faiss_index/index.pkl")
EMB_MODEL = os.getenv("EMB_MODEL", "text-embedding-3-large")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---------------- SETUP ----------------
print(f"Loading FAISS index from {INDEX_PATH}")
index = faiss.read_index(INDEX_PATH)

print(f"Loading metadata from {META_PATH}")
with open(META_PATH, "rb") as f:
    data = pickle.load(f)

if isinstance(data, dict) and "metadatas" in data and "texts" in data:
    METAS = data["metadatas"]
    TEXTS = data["texts"]
    for i, m in enumerate(METAS):
        m["text"] = TEXTS[i]
else:
    METAS = data
    for m in METAS:
        if "text" not in m:
            m["text"] = m.get("jd", "")

print(f"Loaded {len(METAS)} metadata entries")
print(f"Index has {index.ntotal} vectors; metadata has {len(METAS)} entries.")

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------- EMBEDDING ----------------
def embed_query(text: str) -> np.ndarray:
    """Embed query using OpenAI embedding model"""
    response = client.embeddings.create(
        input=text,
        model=EMB_MODEL
    )
    emb = np.array(response.data[0].embedding, dtype=np.float32)
    emb = emb / np.linalg.norm(emb)
    return emb.reshape(1, -1)

# ---------------- RETRIEVAL ----------------
def retrieve_candidates(query_text, top_k=20, job_level=None, max_duration=None):
    """Retrieve top candidates based on embedding similarity with optional filters"""
    q_emb = embed_query(query_text)
    D, I = index.search(q_emb, top_k * 3)  # fetch more to allow filtering
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(METAS):
            continue
        meta = METAS[idx].copy()
        
        meta["score"] = float(score)

        # Filter by job_level if specified
        # if job_level and meta.get("job_level") and meta["job_level"].lower() != job_level.lower():
        #     continue
        # # Filter by max_duration if specified
        # if max_duration and meta.get("duration_minutes") and meta["duration_minutes"] > max_duration:
        #     continue

        results.append(meta)

    # Sort by similarity
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def infer_job_level_and_duration(query: str):
    """
    Uses LLM to infer:
    - job_level (e.g., graduate, junior, senior)
    - max_duration in minutes
    Returns: (job_level:str or None, max_duration:int or None)
    """
    prompt = f"""
You are an expert at analyzing job descriptions and hiring requirements.

For the following job description or query, detect:
1. Job level (e.g., graduate, junior, mid-level, senior)
2. Recommended maximum assessment duration in minutes

Return JSON ONLY, like:
{{"job_level": "graduate", "max_duration": 45}}

Job description / query:
\"\"\"{query}\"\"\"
"""
    try:
        # Try Responses API
        try:
            res = client.responses.create(model="gpt-4o-mini", input=prompt)
            text = res.output_text.strip()
        except TypeError:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            text = resp.choices[0].message.content.strip()

        # Extract JSON safely
        match = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(match.group(0)) if match else {}

        job_level = data.get("job_level")
        max_duration = data.get("max_duration")
        if isinstance(max_duration, str) and max_duration.isdigit():
            max_duration = int(max_duration)

        return job_level, max_duration

    except Exception as e:
        print("⚠️ Could not infer job_level/max_duration:", e)
        return None, None

# ---------------- LLM RERANKER ----------------
def rerank_llm(query, items, max_recs=10):
    """Rerank candidates using LLM to provide reasoning and relevance scores"""
    if not items:
        return []

    short_catalog = [
        {
            "assessment_name": i.get("assessment_name", ""),
            "url": i.get("url", ""),
            "summary": (i.get("text") or "")[:200],
        }
        for i in items
    ]

    prompt = f"""
You are an SHL assessment recommender.
Given a job description and candidate assessments, select and rank the top {max_recs} relevant ones.

Return ONLY valid JSON array like:
[
  {{
    "assessment_name": "string",
    "url": "string",
    "reason": "short justification",
    "relevance_score": 0.0 to 1.0
  }}
]

JOB DESCRIPTION:
{query}

ASSESSMENT CANDIDATES:
{json.dumps(short_catalog, indent=2)}
"""

    try:
        # Try Responses API first
        try:
            res = client.responses.create(model="gpt-4o-mini", input=prompt)
            text = res.output_text.strip()
        except TypeError:
            # Fallback to chat completions
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            text = resp.choices[0].message.content.strip()

        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        data = json.loads(match.group(1)) if match else []

        if isinstance(data, dict) and "recommendations" in data:
            recs = data["recommendations"]
        elif isinstance(data, list):
            recs = data
        else:
            recs = []

        if not recs:
            raise ValueError("No valid recommendations from LLM")

        return recs[:max_recs]

    except Exception as e:
        print(f"⚠️ LLM rerank fallback: {e}")
        return [
            {
                "assessment_name": i.get("assessment_name", ""),
                "url": i.get("url", ""),
                "reason": "Based on FAISS similarity (fallback).",
                "relevance_score": round((i["score"] + 1) / 2, 3),
            }
            for i in items[:max_recs]
        ]

# ---------------- MAIN RECOMMENDER ----------------
def get_recommendations(query_text, max_recs=5, use_llm=True):
    # Step 1: infer job_level and max_duration
    job_level, max_duration = infer_job_level_and_duration(query_text)
    print(f"🧭 Inferred job_level: {job_level}, max_duration: {max_duration} minutes")

    # Step 2: retrieve candidates
    candidates = retrieve_candidates(query_text, top_k=max_recs*3, job_level=job_level, max_duration=max_duration)
    # print(cand)
    if not candidates:
        print("⚠️ No candidates found for this query/filters.")
        return []

    # Step 3: rerank with LLM
    if use_llm and OPENAI_API_KEY:
        try:
            print("🤖 Using LLM reranker for final selection...")
            return rerank_llm(query_text, candidates, max_recs=max_recs)
        except Exception as e:
            print("⚠️ LLM rerank failed:", e)

    # Fallback
    return [
        {
            "assessment_name": c.get("assessment_name", ""),
            "url": c.get("url", ""),
            "reason": "",
            "relevance_score": max(0.0, min(1.0, (c["score"] + 1) / 2))
        }
        for c in candidates[:max_recs]
    ]

# ---------------- CLI TEST ----------------
if __name__ == "__main__":
    query = input("Enter a job description or role title: ").strip()

    print(f"\n🔍 Query: {query}\n")
    results = get_recommendations(query, max_recs=10, use_llm=True)
    print(json.dumps(results, indent=2))

