import os
import json
import pickle
import faiss
import numpy as np
import pandas as pd
from openai import OpenAI

# === CONFIGURATION ===
INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/faiss_index/index.faiss")
META_PATH = os.getenv("META_PATH", "data/faiss_index/index.pkl")
EMB_MODEL = os.getenv("EMB_MODEL", "text-embedding-3-large")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EXCEL_PATH = os.getenv("QUERY_FILE", "Evaluations/Gen_AI Dataset.xlsx")  # Input Excel
EXCEL_SHEET = os.getenv("QUERY_SHEET", "Queries")  # Sheet name
OUTPUT_CSV = os.getenv("OUTPUT_FILE", "retrieval_only.csv")

# === LOAD INDEX + METADATA ===
print(f"📂 Loading FAISS index from {INDEX_PATH} ...")
index = faiss.read_index(INDEX_PATH)

print(f"📦 Loading metadata from {META_PATH} ...")
with open(META_PATH, "rb") as f:
    data = pickle.load(f)

# Handle both dictionary or list-based formats
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

print(f"✅ Loaded {len(METAS)} metadata entries.")
print(f"✅ FAISS index contains {index.ntotal} vectors.\n")

# === EMBEDDING CLIENT ===
client = OpenAI(api_key=OPENAI_API_KEY)

def embed_query(text: str) -> np.ndarray:
    """Embed a single query using OpenAI embeddings."""
    response = client.embeddings.create(input=text, model=EMB_MODEL)
    emb = np.array(response.data[0].embedding, dtype=np.float32)
    emb /= np.linalg.norm(emb)
    return emb.reshape(1, -1)

def retrieve(query_text, top_k=10):
    """Retrieve top_k most similar items from FAISS."""
    q_emb = embed_query(query_text)
    D, I = index.search(q_emb, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(METAS):
            continue
        meta = METAS[idx].copy()
        meta["score"] = float(score)
        results.append(meta)
    return sorted(results, key=lambda x: x["score"], reverse=True)


# === MAIN EXECUTION ===
def main():
    print(f"📘 Reading Excel file: {EXCEL_PATH}")

    df = pd.read_excel(EXCEL_PATH, sheet_name="Train-Set")
    df.columns = df.columns.str.strip().str.lower()

    if "query" not in df.columns:
        raise ValueError(f"Excel must have a column named 'query'. Found: {df.columns.tolist()}")

    # ✅ Group by unique query
    grouped = df.groupby("query")
    results_data = []

    print(f"🔍 Running retrieval for {len(grouped)} unique queries from sheet 'Train-Set'...\n")

    for qid, (query_text, group) in enumerate(grouped, start=1):
        print(f"➡️ Query {qid}: {query_text[:80]}...")

        # Run retrieval ONCE per query
        retrieved = retrieve(query_text, top_k=10)

        # List all ground-truth URLs for this query
        ground_truth_urls = group["Assessment_url"].dropna().unique().tolist()

        # Store retrieved results (10 per query)
        for rank, rec in enumerate(retrieved, start=1):
            results_data.append({
                "Query ID": qid,
                "Query": query_text,
                "Retrieved Rank": rank,
                "Retrieved URL": rec.get("url", ""),
                "Retrieved Score": rec.get("score", ""),
                "Ground Truth URLs": "; ".join(ground_truth_urls),
                "Assessment Name": rec.get("assessment_name", ""),
                "Test Type": rec.get("test_type", ""),
                "Duration": rec.get("duration", ""),
                "Job Level": rec.get("job_levels", ""),
                "Remote Support": rec.get("remote_support", ""),
            })

    out_df = pd.DataFrame(results_data)
    out_df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n✅ Retrieval results saved to {OUTPUT_CSV}")
    print(f"💾 {len(out_df)} rows written (covering {len(grouped)} unique queries).")



if __name__ == "__main__":
    main()
