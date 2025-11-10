import os
import pandas as pd
import pickle
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import faiss
import tqdm

# Paths to your CSVs
FACT_SHEET_CSV = "./Scraping/shl_fact_sheets_text.csv"
DETAILS_CSV = "./Scraping/shl_assessments_details.csv"

# Output directory
OUTPUT_DIR = "./data/faiss_index"
INDEX_PATH = os.path.join(OUTPUT_DIR, "index.faiss")
META_PATH = os.path.join(OUTPUT_DIR, "index.pkl")

# -------------------------------
# 1. Load and merge data
# -------------------------------
def load_and_merge_data():
    fact_df = pd.read_csv(FACT_SHEET_CSV)
    details_df = pd.read_csv(DETAILS_CSV)

    # Merge both datasets on URL
    merged_df = pd.merge(details_df, fact_df, on="url", how="outer").fillna("")

    # Combine all available text sources
    merged_df["jd"] = merged_df.apply(
        lambda row: (
            (
                row.get("description", "").strip() or row.get("fact_sheet_text", "").strip()
            ).strip()
        ),
        axis=1
    )

    # Safely keep only available columns
    keep_cols = [col for col in ["assessment_name_x", "url", "jd",  'job_levels', 'languages', 'assessment_length','remote_testing_x','adaptive_x','test_type_x' ] if col in merged_df.columns]
    merged_df = merged_df[keep_cols]

    # Filter out empty text
    merged_df = merged_df[merged_df["jd"].str.strip() != ""]

    print(f"✅ Loaded {len(merged_df)} rows with columns: {keep_cols}")
    return merged_df



def build_doc_text(row):
    """Create a semantically rich description for embedding."""
    name = row.get("assessment_name_x", "")
    desc = row.get("jd", "")
    level = row.get("job_levels", "")
    lang = row.get("languages", "")
    duration = row.get("assessment_length", "")
    remote = row.get("remote_testing_x", "")
    adaptive = row.get("adaptive_x", "")
    ttype = row.get("test_type_x", "")

    # Turn structured data into readable context
    text = f"""
    Description: {desc}
    Suitable Job Levels: {level}
    This assessment measures key skills, behaviors, and knowledge areas relevant to its category.
    """
    return text.strip()
# -------------------------------
# 2. Build and save FAISS index
# -------------------------------
def ingest_to_faiss(merged_df):
    print("Creating FAISS index...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=os.getenv("OPENAI_API_KEY")  # use env var, not hardcoded key
    )

    documents = []
    for _, row in merged_df.iterrows():
        metadata = {
            "assessment_name": row.get("assessment_name_x", ""),
            "url": row.get("url", ""),
            "test_type": row.get("test_type_x", ""),
            "job_levels": row.get("job_levels", "")
        }
        documents.append(Document(
            page_content=build_doc_text(row),
            metadata={
                "assessment_name": row.get("assessment_name_x", ""),
                "url": row.get("url", ""),
                "test_type": row.get("test_type_x", ""),
                "job_levels": row.get("job_levels", ""),
                "duration": row.get("assessment_length", ""),
                "remote_support": row.get("remote_testing_x", ""),
                "adaptive_support": row.get("adaptive_x", ""),
            }
        ))
    db = FAISS.from_documents(documents, embeddings)

    # Save FAISS index manually
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    faiss.write_index(db.index, os.path.join(OUTPUT_DIR, "index.faiss"))

    # Save metadata manually (metadatas + texts)
    with open(os.path.join(OUTPUT_DIR, "index.pkl"), "wb") as f:
        pickle.dump({
            "metadatas": [d.metadata for d in documents],
            "texts": [d.page_content for d in documents]
        }, f)

    print(f"✅ FAISS index and metadata saved to: {OUTPUT_DIR}")

# -------------------------------
# 3. Verify FAISS index integrity
# -------------------------------
def verify_faiss_integrity():
    print(f"\nVerifying saved FAISS index...")

    print(f"Loading FAISS index from {INDEX_PATH}")
    index = faiss.read_index(INDEX_PATH)

    print(f"Loading metadata from {META_PATH}")
    with open(META_PATH, "rb") as f:
        metas = pickle.load(f)

    if isinstance(metas, dict) and "metadatas" in metas:
        metas = metas["metadatas"]

    print(f"Loaded {len(metas)} metadata entries")
    print(f"Index has {index.ntotal} vectors; metadata has {len(metas)} entries.")

    if index.ntotal != len(metas):
        print("WARNING: Index and metadata counts do NOT match!")
    else:
        print("FAISS and metadata counts match perfectly!")

# -------------------------------
# 4. Main script
# -------------------------------
def main():
    merged_df = load_and_merge_data()
    print(f"Loaded {len(merged_df)} assessments for ingestion.")
    merged_df.to_csv('merged.csv', index=False)
    ingest_to_faiss(merged_df)
    verify_faiss_integrity()

if __name__ == "__main__":
    main()
