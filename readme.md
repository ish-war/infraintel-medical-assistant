# RAG Medical Assistant

![Project Banner](./images/banner.png) <!-- Add your main UI or project banner image here -->

---

## Overview

The **RAG Medical Assistant** is a cloud-ready, AI-driven medical assistant that leverages Retrieval-Augmented Generation (RAG) and Google's Gemini AI to provide structured, context-aware answers to medical queries.  

The project consists of three main components:

1. **Document AI (Task 1)** – Extracts structured data from medical documents.
2. **Summarization (Task 2)** – Summarizes extracted documents into structured patient summaries.
3. **RAG Agent (Task 3)** – Answers user queries using the summaries and optionally enhances responses with Gemini AI.

This main repository ties all three tasks together and provides a **FastAPI-based web interface** for user interaction.

---

## Features

- User-friendly **web UI** to ask medical questions.
- Retrieval of relevant medical summaries based on user queries.
- Optional integration with **Gemini AI** for enhanced, human-like answers.
- Fully **containerized with Docker** and deployable to **GCP Cloud Run**.
- Modular structure for easy maintenance and extension.

---

## Project Structure

```bash
infraintel/ # Root folder
├─ .env # Environment variables and API keys
├─ Dockerfile # Docker build file
├─ requirements.txt # Python dependencies
├─ main.py # Entry script for Document AI
├─ config/
│ └─ settings.py # Configuration for API keys, paths, etc.
├─ document_ai/ # Task 1: Document AI extraction
├─ summarize/ # Task 2: Summarization
│ └─ summaries/ # Generated summary JSONs
├─ rag_agent/ # Task 3: RAG agent & FastAPI UI
│ ├─ api/
│ │ └─ fastapi_app.py # FastAPI application
│ ├─ services/ # LLM & RAG utilities
│ ├─ vectorstore/ # FAISS index files
│ ├─ static/ # CSS, JS files
│ └─ templates/ # HTML templates (UI)
```


---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ish-war/infraintel-medical-assistant
cd infraintel-medical-assistant
```

### 2. Create .env File

```bash
GCP_PROJECT_ID=<your_project_id>
GCP_PROCESSOR_ID=<your_processor_id>
GCP_LOCATION=<gcp_location for processor> (us, eu)
GCS_BUCKET_NAME=<your_bucket_name>
GCS_OUTPUT_BUCKET=<your_output_bucket>
GOOGLE_APPLICATION_CREDENTIALS=<key_path>key.json
GOOGLE_API_KEY=<your_gemini_api_key>
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Build and Run Locally with Docker

```bash
docker build -t rag-medical-assistant .
docker run -p 8000:8000 rag-medical-assistant
```

- Open UI → http://localhost:8000


--- 

## Usage

### Home Page

<img width="1285" height="896" alt="Screenshot 2025-09-29 212853" src="https://github.com/user-attachments/assets/50fcf504-45d5-45bf-b506-70b89295b488" />

- Enter your medical question.

- Optionally check Use Gemini AI.

- Click Ask to retrieve structured answers.

### Results Page

<img width="1361" height="919" alt="Screenshot 2025-09-29 213003" src="https://github.com/user-attachments/assets/0a47536c-0b90-43fa-ba32-aa8f33839146" />

- Shows retrieved records from the database.

- Displays Gemini-generated answer (if enabled).

- Clean, responsive UI with clear separation of metadata.

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

## Deployment

The project is containerized with Docker and can be deployed to Google Cloud Run:

- Enable required GCP APIs: Cloud Run, Artifact Registry, Cloud Build.

- Push Docker image to Artifact Registry.

- Deploy image to Cloud Run to get a public endpoint.

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


## Contributing

- Fork the repository and create a new branch for your feature or bugfix.

- Ensure code follows Python PEP8 standards.

- Test your changes locally before submitting a pull request.

## License

This project is licensed under the MIT License. See LICENSE
 for details.
 
