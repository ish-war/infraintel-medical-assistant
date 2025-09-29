# rag_agent/services/rag_utils.py
import os
import json
from typing import List, Tuple, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Paths (adjust if you want)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # intraintel/
SUMMARIES_DIR = os.path.join(BASE_DIR, "summarize", "summaries")  # where Task2 .json files live
VSTORE_DIR = os.path.join(BASE_DIR, "rag_agent", "vectorstore")
os.makedirs(VSTORE_DIR, exist_ok=True)

SUMMARY_INDEX_FILE = os.path.join(VSTORE_DIR, "summary_index.index")
SUMMARY_TEXTS_FILE = os.path.join(VSTORE_DIR, "summary_texts.npy")
SUMMARY_METADATA_FILE = os.path.join(VSTORE_DIR, "summary_metadata.json")

# Embedding model (same family as Task1 to keep similarity behaviour consistent)
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBED_DIM = 384  # dimension for all-MiniLM-L6-v2

# lazy model loader
_embedder = None


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_NAME)
    return _embedder


def load_summaries_from_folder(summaries_dir: str = SUMMARIES_DIR) -> List[Dict[str, Any]]:
    """
    Load all JSON summary files from the summaries folder.
    Expect each file to be a JSON with at least a "summary" object that contains Patient, Diagnosis, Treatment, Follow-up.
    Returns a list of metadata dicts (one per file) in deterministic order.
    """
    files = sorted(
        [
            os.path.join(summaries_dir, f)
            for f in os.listdir(summaries_dir)
            if f.lower().endswith(".json")
        ]
    )
    summaries = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                # keep entire record as metadata; ensure 'summary' key exists
                summaries.append(data)
        except Exception as e:
            print(f"Warning: failed to load {fp}: {e}")
    return summaries


def summary_to_text(metadata: Dict[str, Any]) -> str:
    """
    Convert a metadata JSON to a single text string to embed.
    Keep fields in a consistent order so embeddings are consistent.
    """
    s = metadata.get("summary", {})
    patient = s.get("Patient", "")
    diagnosis = s.get("Diagnosis", "")
    treatment = s.get("Treatment", "")
    follow_up = s.get("Follow-up", "")

    # Build a concise representation
    text = (
        f"Patient: {patient}\n"
        f"Diagnosis: {diagnosis}\n"
        f"Treatment: {treatment}\n"
        f"Follow-up: {follow_up}"
    )
    return text


def build_summary_index(
    summaries_dir: str = SUMMARIES_DIR,
    index_file: str = SUMMARY_INDEX_FILE,
    texts_file: str = SUMMARY_TEXTS_FILE,
    metadata_file: str = SUMMARY_METADATA_FILE,
    embed_model_name: str = EMBED_MODEL_NAME,
    embed_dim: int = EMBED_DIM,
) -> Tuple[faiss.IndexFlatL2, List[str], List[Dict[str, Any]]]:
    """
    Build a FAISS index from the summary JSON files.
    Saves index, texts (.npy) and metadata (.json) to VSTORE_DIR.
    Returns (index, texts_list, metadata_list).
    """
    print("Loading summary JSON files...")
    metadata_list = load_summaries_from_folder(summaries_dir)
    if not metadata_list:
        raise RuntimeError(f"No summaries found in {summaries_dir} — please run Task 2 first.")

    print(f"Found {len(metadata_list)} summary files. Converting to text for embedding...")
    texts = [summary_to_text(m) for m in metadata_list]

    # embed all texts (batch)
    embedder = get_embedder()
    print("Computing embeddings (this may take a bit on first run)...")
    vectors = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    # build FAISS index
    print("Building FAISS index...")
    index = faiss.IndexFlatL2(embed_dim)
    index.add(vectors)

    # persist index and data
    print(f"Saving index to {index_file} ...")
    faiss.write_index(index, index_file)
    np.save(texts_file, np.array(texts, dtype=object))
    with open(metadata_file, "w", encoding="utf-8") as fh:
        json.dump(metadata_list, fh, ensure_ascii=False, indent=2)

    print("Summary FAISS index built and saved.")
    return index, texts, metadata_list


def load_summary_index(
    index_file: str = SUMMARY_INDEX_FILE,
    texts_file: str = SUMMARY_TEXTS_FILE,
    metadata_file: str = SUMMARY_METADATA_FILE,
) -> Tuple[faiss.IndexFlatL2, List[str], List[Dict[str, Any]]]:
    """
    Load the summary index, texts and metadata from disk.
    Returns (index, texts_list, metadata_list)
    """
    if not os.path.exists(index_file):
        raise FileNotFoundError(f"Summary index not found at {index_file}. Run build_summary_index().")
    index = faiss.read_index(index_file)

    texts = []
    if os.path.exists(texts_file):
        texts = np.load(texts_file, allow_pickle=True).tolist()
    else:
        print("Warning: texts.npy not found for summaries; continuing with empty texts list.")

    metadata_list = []
    if os.path.exists(metadata_file):
        with open(metadata_file, "r", encoding="utf-8") as fh:
            metadata_list = json.load(fh)
    else:
        print("Warning: metadata.json not found for summaries; continuing with empty metadata list.")

    return index, texts, metadata_list


def search_summary_index(
    query_text: str,
    top_k: int = 5,
    index: faiss.Index = None,
    metadata_list: List[Dict] = None,
):
    """
    Convenience search: embed query, run FAISS search and return list of (metadata, distance) for top_k.
    If index/metadata_list are not provided, load from disk.
    """
    if index is None or metadata_list is None:
        index, _, metadata_list = load_summary_index()

    embedder = get_embedder()
    q_vec = embedder.encode([query_text], convert_to_numpy=True)
    distances, indices = index.search(q_vec, top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < len(metadata_list):
            results.append({"metadata": metadata_list[idx], "distance": float(dist)})
    return results


if __name__ == "__main__":
    build_summary_index()
