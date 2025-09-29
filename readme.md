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

Open [Link](http://localhost:8000) in your browser.

## Usage

### Home Page

<!-- Add screenshot of index.html -->

- Enter your medical question.

- Optionally check Use Gemini AI.

- Click Ask to retrieve structured answers.

### Results Page

<!-- Add screenshot of results.html -->

- Shows retrieved records from the database.

- Displays Gemini-generated answer (if enabled).

- Clean, responsive UI with clear separation of metadata.

## Deployment

The project is containerized with Docker and can be deployed to Google Cloud Run:

- Enable required GCP APIs: Cloud Run, Artifact Registry, Cloud Build.

- Push Docker image to Artifact Registry.

- Deploy image to Cloud Run to get a public endpoint.

## Contributing

- Fork the repository and create a new branch for your feature or bugfix.

- Ensure code follows Python PEP8 standards.

- Test your changes locally before submitting a pull request.

## License

This project is licensed under the MIT License. See LICENSE
 for details.
 
