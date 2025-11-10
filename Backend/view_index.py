import os
import faiss
import pickle
from pathlib import Path

# Try new LangChain imports if available
try:
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


def view_chunks():
    base_path = Path("data/faiss_index")
    index_file = base_path / "index.faiss"
    meta_file = base_path / "index.pkl"

    print("🔍 Loading FAISS vector store from disk...\n")

    # --- Try LangChain FAISS first ---
    if LANGCHAIN_AVAILABLE and (base_path / "index.pkl").exists():
        try:
            print("Attempting to load LangChain FAISS index...")
            embeddings = OpenAIEmbeddings()
            vector_store = FAISS.load_local(
                str(base_path),
                embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"✅ Loaded LangChain FAISS index successfully.")
            print(f"Total chunks: {len(vector_store.docstore._dict)}\n")

            for i, (k, v) in enumerate(vector_store.docstore._dict.items()):
                print(f"[{i}] {v.page_content[:250]}...\n")
                if i >= 5:
                    break
            return
        except Exception as e:
            print(f"⚠️ LangChain FAISS load failed: {e}\nFalling back to raw FAISS...")

    # --- Fallback: raw FAISS + pickle ---
    print("Loading raw FAISS index + pickle metadata...")

    if not index_file.exists() or not meta_file.exists():
        raise FileNotFoundError(f"❌ Missing FAISS index or metadata: {index_file}, {meta_file}")

    index = faiss.read_index(str(index_file))
    with open(meta_file, "rb") as f:
        metadata = pickle.load(f)

    # Handle both possible metadata formats
    if isinstance(metadata, dict) and "metadatas" in metadata and "texts" in metadata:
        metas = metadata["metadatas"]
        texts = metadata["texts"]
        for i, m in enumerate(metas):
            m["text"] = texts[i]
    else:
        metas = metadata
        for m in metas:
            if "text" not in m and "jd" in m:
                m["text"] = m["jd"]

    print(f"✅ Loaded raw FAISS index successfully.")
    print(f"Total entries: {len(metas)}\n")

    for i, m in enumerate(metas[:6]):
        print(f"[{i}] {m.get('assessment_name', 'Unnamed')} | {m.get('test_type', 'N/A')}")
        print(m.get('text', '')[:250])
        print("-" * 60)


if __name__ == "__main__":
    view_chunks()
