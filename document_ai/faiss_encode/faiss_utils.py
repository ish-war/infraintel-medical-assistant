import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ----------------- Settings -----------------
FAISS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faiss")
FAISS_INDEX_FILE = os.path.join(FAISS_FOLDER, "document_embeddings.index")
TEXTS_FILE = os.path.join(FAISS_FOLDER, "texts.npy")
os.makedirs(FAISS_FOLDER, exist_ok=True)

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# ----------------- Load or Initialize -----------------
# Load FAISS index
def create_or_load_faiss_index(dim: int = 384):
    if os.path.exists(FAISS_INDEX_FILE):
        index = faiss.read_index(FAISS_INDEX_FILE)
        print("Loaded existing FAISS index.")
    else:
        index = faiss.IndexFlatL2(dim)
        print("Created new FAISS index.")
    return index

# Load stored texts
if os.path.exists(TEXTS_FILE):
    stored_texts = list(np.load(TEXTS_FILE, allow_pickle=True))
else:
    stored_texts = []

# ----------------- Functions -----------------
def add_text_to_faiss(text: str, index=None):
    """Add a text to FAISS index and store the text."""
    global stored_texts

    if not text.strip():
        return index

    if index is None:
        index = create_or_load_faiss_index()

    # Encode text and add to FAISS
    vector = embed_model.encode([text], convert_to_numpy=True)
    index.add(vector)

    # Store text for retrieval
    stored_texts.append(text)
    np.save(TEXTS_FILE, np.array(stored_texts, dtype=object))

    return index

def save_faiss_index(index):
    """Save FAISS index to disk."""
    faiss.write_index(index, FAISS_INDEX_FILE)
    np.save(TEXTS_FILE, np.array(stored_texts, dtype=object))
    print(f"FAISS index saved to {FAISS_INDEX_FILE} and texts saved to {TEXTS_FILE}")
