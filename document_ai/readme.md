# Document AI + FAISS Search API 🚀

A production-ready project to extract text from documents/images stored in Google Cloud Storage using **Google Document AI**, store them in a **FAISS vector database**, and provide a **search API** to retrieve relevant content by keyword.

---

## Features

- Batch processing of documents/images from a GCS bucket using Google Document AI.
- Support for multiple image types: `JPEG` and `PNG`.
- Text embeddings generated using **Sentence Transformers (`all-MiniLM-L6-v2`)**.
- Store embeddings in a **FAISS** vector database for fast similarity search.
- FastAPI-based API for:
  - Triggering batch document processing.
  - Searching for documents by keyword/query.
- Simple raw text retrieval from FAISS (can be extended with LLMs later).

---

## Folder Structure

```bash
intraintel/
├── config/
│ └── settings.py # GCP & bucket configurations
├── faiss_encode/
│ ├── init.py
│ └── faiss_utils.py # FAISS creation, text embedding, indexing
├── services/
│ ├── batch_process.py # Batch processing documents from GCS
├── faiss/ # FAISS index stored here
├── main.py # FastAPI app entry point
├── requirements.txt # Python dependencies
└── README.md
```


---

## Prerequisites

- Python 3.9+
- Google Cloud Project with **Document AI** enabled.
- GCS bucket for input and output documents.
- Service account key with `Document AI Admin` and `Storage Admin` permissions.
- `.env` file with the following keys:

```bash
GCP_PROJECT_ID=your-project-id
GCP_PROCESSOR_ID=your-processor-id
GCP_LOCATION=us
GCS_BUCKET_NAME=your-gcp-bucket-name
GCP_OUTPUT_BUCKET=your-output-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=C:/<your_path>/key.json
GOOGLE_API_KEY=your_api_key
```


---

## Setup

1. **Clone the repository**

```bash
git clone <repo-url>
cd intraintel
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Set Google Credentials**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"  # Linux/Mac
set GOOGLE_APPLICATION_CREDENTIALS=path\to\your\service-account-key.json      # Windows
```

5. **Prepare FAISS Folder**
```bash
mkdir faiss
```

## Running the Application

```bash
uvicorn main:app --reload

Access the app at: http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs
```

**Search**

Search your FAISS index for relevant content by keyword/query:

```bash
POST /search
Content-Type: application/json

{
  "query": "fever",
  "top_k": 5
}
```

## Notes

- Supported file types: .jpg, .jpeg, .png.

- FAISS index is stored locally in faiss/document_embeddings.index.

- The current search returns raw text. Can be extended to use an LLM for structured answers.

- Ensure your GCS input bucket has proper read access and the output bucket has write access.

## Dependencies

```bash
fastapi

uvicorn

google-cloud-documentai

google-cloud-storage

sentence-transformers

faiss-cpu

pydantic
```

## License

MIT License


