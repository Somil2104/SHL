import os
import json
import pickle
import faiss
import numpy as np
from openai import OpenAI
import openai
import re
from collections import defaultdict

INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/faiss_index/index.faiss")
META_PATH = os.getenv("META_PATH", "data/faiss_index/index.pkl")
EMB_MODEL = os.getenv("EMB_MODEL", "text-embedding-3-large")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(f"Loading FAISS index from {INDEX_PATH}")
index = faiss.read_index(INDEX_PATH)

print(f"Loading metadata from {META_PATH}")
with open(META_PATH, "rb") as f:
    data = pickle.load(f)

if isinstance(data, dict) and "metadatas" in data and "texts" in data:
    METAS = data["metadatas"]
    TEXTS = data["texts"]
    for i, m in enumerate(METAS):
        m["jd"] = TEXTS[i]
else:
    METAS = data
    for m in METAS:
        if "jd" not in m:
            m["jd"] = ""

print(f"Loaded {len(METAS)} metadata entries")
print(f"Index has {index.ntotal} vectors; metadata has {len(METAS)} entries.")

client = OpenAI(api_key=OPENAI_API_KEY)

TEST_TYPE_MAP = {
    "ability": "A",
    "aptitude": "A",
    "biodata": "B",
    "situational": "B",
    "competency": "C",
    "competencies": "C",
    "development": "D",
    "360": "D",
    "assessment": "E",
    "exercise": "E",
    "knowledge": "K",
    "skills": "K",
    "personality": "P",
    "behavior": "P",
    "simulation": "S",
}

def normalize_test_type(t: str):
    t = t.lower().strip()
    for key, code in TEST_TYPE_MAP.items():
        if key in t:
            return code
    return "UNK"

def embed_query(text: str) -> np.ndarray:
    """Embed query using OpenAI embedding model"""
    response = client.embeddings.create(
        input=text,
        model=EMB_MODEL
    )
    emb = np.array(response.data[0].embedding, dtype=np.float32)
    emb = emb / np.linalg.norm(emb)  # Normalize for cosine sim
    return emb.reshape(1, -1)

def retrieve(query_text, top_k=20):
    q_emb = embed_query(query_text)
    D, I = index.search(q_emb, top_k)
    out = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(METAS): continue
        meta = METAS[idx].copy()
        meta["score"] = float(score)
        out.append(meta)
    return sorted(out, key=lambda x: x["score"], reverse=True)

TEST_TYPE_DESCRIPTIONS = """
A: Ability & Aptitude – reasoning, numerical, or problem-solving.
B: Biodata & Situational Judgement – background or judgment-based.
C: Competencies – role-specific behavioral competencies.
D: Development & 360 – feedback and development-related.
E: Assessment Exercises – role-play or case study assessments.
K: Knowledge & Skills – technical, coding, or functional skills.
P: Personality & Behavior – communication, teamwork, leadership.
S: Simulations – realistic job simulations or scenario exercises.
"""

def classify_query_domains(query: str):
    prompt = f"""
You are an expert at mapping job description queries to SHL test categories. According to the job requirement, analyze what all assessments are required.

Available test type codes:
A = Ability
B = Biodata/Situational
C = Competency
D = Development
E = Assessment Exercise
K = Knowledge & Skills
P = Personality & Behavior
S = Simulation

Return ONLY valid JSON like:
{{"relevant_test_types": ["K", "P"]}}

Query: "{query}"
"""
    try:
        # ---- Try new SDK first ----
        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
                temperature=0,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.output_text)
        except TypeError:
            # ---- Fallback for older SDK ----
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            text = resp.choices[0].message.content.strip()
            data = json.loads(text[text.find("{"):text.rfind("}") + 1])

        return data.get("relevant_test_types", ["K"])
    except Exception as e:
        print("⚠️ LLM classification failed, fallback to ['K']:", e)
        return ["K"]

from openai import OpenAI
import json, os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_rerank(query_text, retrieved_items, max_recs=10):
    """
    Use LLM to rerank retrieved items based on relevance to the query.
    """
    # Create compact input summary for the LLM
    catalog_summary = [
        {
            "assessment_name": i.get("assessment_name"),
            "test_type": i.get("test_type"),
            "url": i.get("url"),
            "jd": (i.get("jd") or "")[:300],
            "time_duration": i.get("duration"),
            "job_level": i.get("job_levels"),
            "remote_support": i.get("remote_support", ""),
            "adaptive_support": i.get("adaptive_support", ""),
        }
        for i in retrieved_items
    ]
    prompt = f"""
You are an expert recommender system for SHL assessments.
Rerank the following assessments by relevance to the user's hiring query. Consider the duration and job level. If it is not given but jd highly matches with the requirement, give it a priority. Also focus on the skills it offer using test_type. If more than one jd looks similar, pick the one with more relevance with respect to other factors like test type, job level, adaptive support or remote support.
For each, output:
- assessment_name
- url
- jd
- duration
- job level
- remote support
- adaptive support
- test type
- short_reason (1-2 sentences)
- relevance_score (float between 0 and 1)

Return ONLY valid JSON list, nothing else.
Example:
[
  {{
    "assessment_name": "Java Developer (Advanced)",
    "url": "https://www.shl.com/products/java-advanced/",
    "adaptive_support": "Yes",
    "description": Job is about Java developer,
    "duration": 10 mins,
    "remote_support": "Yes",
    "test_type": K, A,
    "short_reason": "Tests advanced Java skills relevant to the query.",
    "relevance_score": 0.95
  }}
]

User Query:
\"\"\"{query_text}\"\"\"

Assessments:
{json.dumps(catalog_summary, indent=2)}
"""

    try:
        response = client.responses.create(
            model='gpt-4.1',
            input=prompt
        )
        text = response.output_text.strip()

        # Try to directly parse JSON
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # Try to extract valid JSON substring
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
            else:
                raise ValueError(f"Cannot parse JSON from reranker output: {text[:200]}")
        reranked = sorted(parsed, key=lambda x: x.get("relevance_score", 0), reverse=True)
        return reranked[:max_recs]

    except Exception as e:
        print(f"LLM rerank failed: {e}")
        fallback = retrieved_items[:max_recs]
        for f in fallback:
            f["short_reason"] = "Based on embedding similarity (fallback)."
            f["relevance_score"] = 0.0
        return fallback

def get_recommendations(query_text, max_recs=5, use_llm=True):
    candidates = retrieve(  query_text, top_k=30)
    if use_llm and OPENAI_API_KEY:
        try:
            print("Using LLM reranker...")
            return llm_rerank(query_text,candidates, max_recs=max_recs)
        except Exception as e:
            print("LLM rerank failed:", e)

    print("Using similarity-based fallback.")
    sorted_c = sorted(candidates, key=lambda x: x["score"], reverse=True)[:max_recs]
    return [
        {
            "assessment_name": c.get("assessment_name", ""),
            "url": c.get("url", ""),
            "adaptive_support": c.get("adaptive_support", "No"),
            "description": c.get("jd", ""),
            "duration": c.get("duration", ""),
            "remote_support": c.get("remote_support", "No"),
            "test_type": c.get("test_type", []),
            "short_reason": "",
            "relevance_score": max(0.0, min(1.0, (c["score"] + 1) / 2))
        }
        for c in sorted_c
    ]

if __name__ == "__main__":
    query = input("Enter a job description or role title: ").strip()
    print("\nRetrieving top recommendations...\n")

    results = get_recommendations(query, max_recs=10, use_llm=True)
    print(json.dumps(results, indent=2))

