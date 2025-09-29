
# 🩺 RAG Medical Assistant – Task 3 (rag_agent)

## Overview

rag_agent is the Retrieval-Augmented Generation (RAG) medical assistant microservice.
It allows users to query structured patient summaries, retrieve relevant records from a vector store, and optionally synthesize answers using Gemini AI.

This service provides both:

- Web UI (FastAPI + Jinja2 templates)

- REST API endpoints for integration with external applications

---

## Features

- RAG-based retrieval from FAISS vector index

- Dynamic answer synthesis using Google Gemini (gemini-2.5-flash)

- FastAPI web interface with Bootstrap-styled UI

- JSON API endpoints for programmatic use

- Handles missing or incomplete data gracefully

---

## Project Structure

```bash
rag_agent/
│
├── api/
│   └── fastapi_app.py      # FastAPI app (UI + API routes)
│
├── services/
│   ├── llm_agent.py        # LLM answer synthesis + RAG pipeline
│   └── rag_utils.py        # FAISS index load/search helpers
│
├── static/
│   └── css/style.css       # Custom UI styles
│
├── templates/
│   ├── base.html           # Layout template
│   ├── index.html          # Home page (query input)
│   └── results.html        # Results display page
│
├── vectorstore/
│   ├── summary_index.index   # FAISS vector index
│   ├── summary_metadata.json # Metadata for records
│   └── summary_texts.npy     # Encoded text vectors
```

---

## Installation & Setup

1. Clone repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>/rag_agent
```

2. Create virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate    # On Linux/Mac
venv\Scripts\activate       # On Windows

pip install -r requirements.txt
```

3. Configure environment

Create a .env file in the project root (not inside rag_agent/):
```bash
GOOGLE_API_KEY=your_api_key_here
```

4. Run service locally

```bash
uvicorn rag_agent.api.fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

- Open UI → http://localhost:8000
- Test API → http://localhost:8000/docs

---

## API Endpoints

### UI

- / → Home page

- /ask-ui → Submit queries via UI

### REST API

- GET /api → Service status

- POST /ask

Request:
```bash
{
  "question": "List patients with fever",
  "top_k": 2,
  "use_gemini": true
}
```
Response:
```bash
{
  "retrieved": [...],
  "retrieved_count": 2,
  "answer": "The top 2 patients with fever are Jyoti Shah, Yaw Han"
}
```

--- 

## Screenshots

<img width="1285" height="896" alt="Screenshot 2025-09-29 212853" src="https://github.com/user-attachments/assets/514cf594-76c1-43fa-b007-2989a55901b5" />

<img width="1361" height="919" alt="Screenshot 2025-09-29 213003" src="https://github.com/user-attachments/assets/bc917e7b-7f82-4d0c-96c5-ccbe7b5b1aee" />

--- 

## Deployment

- Docker

```bash
docker build -t rag-medical-assistant .
docker run -p 8000:8000 rag-medical-assistant
```

- Cloud Run (GCP)

The service is Cloud Run–ready. Once pushed to Artifact Registry, deploy with:
```bash
gcloud run deploy rag-medical-assistant \
  --image us-central1-docker.pkg.dev/<PROJECT_ID>/<REPO_NAME>/rag-medical-assistant:v1 \
  --platform managed --region us-central1 --allow-unauthenticated
```

--- 

## License

This project is licensed under the MIT License – feel free to use and adapt.





