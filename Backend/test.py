import os
import re
import json
import pickle
import faiss
import numpy as np
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings

# -----------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------
FAISS_PATH = "data/faiss_index/index.faiss"
META_PATH = "data/faiss_index/index.pkl"
EMBED_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4.1"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedder = OpenAIEmbeddings(model=EMBED_MODEL, api_key=os.getenv("OPENAI_API_KEY"))


# -----------------------------------------------------
# LOAD INDEX
# -----------------------------------------------------
def load_faiss():
    print("Loading FAISS index and metadata...")
    index = faiss.read_index(FAISS_PATH)
    with open(META_PATH, "rb") as f:
        data = pickle.load(f)

    if isinstance(data, dict) and "metadatas" in data:
        metas = data["metadatas"]
        texts = data["texts"]
    else:
        metas = data
        texts = [""] * len(data)

    print(f"Loaded {len(metas)} entries from FAISS index.")
    return index, metas, texts


index, METAS, TEXTS = load_faiss()


# -----------------------------------------------------
# EMBEDDING + RETRIEVAL
# -----------------------------------------------------
def embed_query(text: str):
    emb = embedder.embed_query(text)
    return np.array(emb).reshape(1, -1)


def retrieve(query_text, top_k=50):
    """Retrieve top_k similar docs using FAISS semantic search"""
    q_emb = embed_query(query_text)
    D, I = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(D[0], I[0]):
        if 0 <= idx < len(METAS):
            meta = METAS[idx].copy()
            meta["score"] = float(score)
            meta["jd"] = TEXTS[idx]
            results.append(meta)

    return results


# -----------------------------------------------------
# LLM CLASSIFICATION
# -----------------------------------------------------
def classify_domains(query_text):
    """
    Use LLM to infer which SHL test domains (A, K, P, etc.) apply to the job description.
    """
    prompt = f"""
You are an expert in HR assessment taxonomy.

Given the following hiring query, identify which SHL test domains are relevant.

Test Type Map:
- A = Ability/Aptitude
- B = Biodata/Situational
- C = Competency
- D = Development/360
- E = Assessment/Exercise
- K = Knowledge/Skills
- P = Personality/Behavior
- S = Simulation

Query:
\"\"\"{query_text}\"\"\"

Return only a JSON list of the detected domain codes, for example: ["K", "P"]
"""

    try:
        response = client.responses.create(model=LLM_MODEL, input=prompt)
        text = response.output_text.strip()

        # Try parsing JSON directly
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\[.*?\]", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                raise ValueError("No valid JSON found")

    except Exception as e:
        print(f"⚠️ LLM classification failed, fallback to ['K']: {e}")
        return ["K"]

# Detected domains for this query: {domains_str}.

# -----------------------------------------------------
# LLM RERANKING
# -----------------------------------------------------
def llm_rerank(query_text, retrieved_items, detected_domains=None, min_recs=5, max_recs=10):
    """
    Use LLM to rerank retrieved items by relevance and ensure domain balance.
    Always return between min_recs and max_recs items.
    """
    domains_str = ", ".join(detected_domains) if detected_domains else "N/A"
    prompt = f"""
You are an expert recommender system for SHL assessments. Determine the best assessements. Rerank the following assessments by how relevant they are to the hiring query below.
Detected job types for this query: {domains_str}. Determine the best assessments based on the job level, job types and time duration.
Ensure a balanced mix of assessments from different detected domains (e.g., technical + behavioral). 

For each recommendation, output:
- assessment_name
- url
- short_reason (1–2 sentences)
- relevance_score (float between 0 and 1)

Return ONLY a valid JSON array. No commentary, no markdown.

User Query:
\"\"\"{query_text}\"\"\"

Assessments:
{json.dumps(retrieved_items[:25], indent=2)}
"""

    try:
        response = client.responses.create(model=LLM_MODEL, input=prompt)
        text = response.output_text.strip()
        ranked = json.loads(text)
        final_results = []

        for r in ranked:
            name = r.get("assessment_name", "").lower()
            match = next(
                (d for d in retrieved_items if d.get("assessment_name", "").lower() == name),
                None
            )
            if match:
                match["short_reason"] = r.get("short_reason", "")
                match["relevance_score"] = r.get("relevance_score", 0)
                final_results.append(match)

        # Ensure coverage for missed domains
        covered_types = {str(r.get("test_type", "")).upper() for r in final_results}
        missing = [d for d in (detected_domains or []) if d not in covered_types]
        if missing:
            print(f"⚠️ LLM missed domains {missing}, adding backups.")
            for m in missing:
                extra = next(
                    (x for x in retrieved_items if str(x.get("test_type", "")).upper() == m),
                    None
                )
                if extra:
                    extra["short_reason"] = "Added for domain balance coverage."
                    extra["relevance_score"] = 0.5
                    final_results.append(extra)

        # Fallback: ensure min_recs count
        if len(final_results) < min_recs:
            additional_needed = min_recs - len(final_results)
            extras = [
                x for x in retrieved_items
                if x not in final_results
            ][:additional_needed]
            for e in extras:
                e["short_reason"] = "Added for list completeness."
                e["relevance_score"] = 0.4
            final_results.extend(extras)

        return final_results[:max_recs]

    except Exception as e:
        print(f"⚠️ LLM rerank failed: {e}")
        fallback = sorted(retrieved_items, key=lambda x: x["score"], reverse=True)[:max_recs]
        return fallback


# -----------------------------------------------------
# MAIN EXECUTION
# -----------------------------------------------------
if __name__ == "__main__":
    query = input("Enter a job description or role title: ").strip()
    print("\nRetrieving top recommendations...\n")

    detected_domains = classify_domains(query)
    print(f"🧭 Detected domains: {detected_domains}")

    retrieved = retrieve(query, top_k=60)
    reranked = llm_rerank(query, retrieved, detected_domains, min_recs=5, max_recs=10)

    print("\n================= RESULTS =================")
    for r in reranked:
        print(f"⭐ {r.get('assessment_name')}")
        print(f"Type: {r.get('test_type')} | URL: {r.get('url')}")
        if "short_reason" in r:
            print(f"Reason: {r['short_reason']}")
        print("-" * 80)
