from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import logging
import faiss

from document_ai.services.batch_process import batch_process_documents
from document_ai.faiss_encode.faiss_utils import create_or_load_faiss_index, embed_model, stored_texts, save_faiss_index


from config.settings import PROJECT_ID, PROCESSOR_ID, LOCATION, GCS_INPUT_URI, GCS_OUTPUT_URI

# ----------------- Setup -----------------
app = FastAPI(title="Document AI + FAISS Search API 🚀")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FAISS index on startup
faiss_index = create_or_load_faiss_index()

# ----------------- Models -----------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# ----------------- Routes -----------------
@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <h1>Welcome to Document AI + FAISS Search API 🚀</h1>
    <p>Use <a href="/docs">/docs</a> to explore the API endpoints.</p>
    """

@app.post("/process/batch")
def process_batch():
    """Trigger batch processing of all files in the input bucket."""
    try:
        batch_process_documents(
            project_id=PROJECT_ID,
            location=LOCATION,
            processor_id=PROCESSOR_ID,
            gcs_input_uri=GCS_INPUT_URI,
            gcs_output_uri=GCS_OUTPUT_URI,
        )
        save_faiss_index(faiss_index)
        return {"status": "Batch processing completed successfully"}
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
def search_faiss(req: SearchRequest):
    """Search FAISS index by query and return raw text from top-k documents."""
    try:
        if faiss_index.ntotal == 0 or len(stored_texts) == 0:
            return {"results": [], "message": "FAISS index is empty"}

        # Encode query
        query_vector = embed_model.encode([req.query], convert_to_numpy=True)

        # Search FAISS
        distances, indices = faiss_index.search(query_vector, req.top_k)

        # Retrieve original texts
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(stored_texts):
                results.append({"text": stored_texts[idx], "distance": float(dist)})

        return {"query": req.query, "results": results, "retrieved_docs_count": len(results)}

    except Exception as e:
        logger.error(f"FAISS search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
