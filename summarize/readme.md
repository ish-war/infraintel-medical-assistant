# Clinical Record Summarization Tool (Task 2)

## Overview
This project provides an automated pipeline to summarize clinical notes into structured JSON outputs for each patient using **Google Gemini LLM** and **FAISS embeddings**. It allows users to process multiple patient records, store individual summaries, and maintain a master index for easy retrieval.

The tool ensures:
- Extraction of relevant patient information such as **Patient Info**, **Diagnosis**, **Treatment**, and **Follow-up** instructions.
- Avoiding duplicate summaries by updating existing patient files if already present.
- Storage of summaries in a dedicated folder for organized access.

---

## Features
- **LLM-based Summarization:** Uses Google Gemini (`gemini-2.5-flash`) to generate structured summaries from clinical notes.
- **FAISS Integration:** Efficiently stores and retrieves clinical notes embeddings for fast access.
- **Dynamic Patient File Handling:** Automatically updates existing patient summaries or creates new files when required.
- **Master Index Creation:** Generates a master JSON file containing all processed patient summaries.
- **Configurable Top-k Retrieval:** Option to summarize all or a limited number of clinical notes.

---

## Notes

- Update .env before running the scripts.

- Summaries for the same patient are updated instead of creating duplicates.

- Works with all clinical notes present in texts.npy.

--- 

## Folder Structure

```bash
infraintel/
│
├─ document_ai/ # FAISS index and texts
│ ├─ faiss/
│ │ ├─ document_embeddings.index
│ │ └─ texts.npy
│
├─ summarize/
│ ├─ services/
│ │ ├─ init.py
│ │ └─ llm_process.py # Main script for summarization
│ └─ summaries/ # JSON outputs for each patient
│
├─ requirements.txt # Project dependencies
├─ .env # Environment variables
├─ main.py # Optional main entry
└─ venv/ # Virtual environment
```

---

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd infraintel
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up Google API Key:

- Add your GOOGLE_API_KEY in .env.
- Call your GOOGLE_API_KEY in config/settings.py.

## Usage

1. Run the summarization script to process all clinical notes:

```bash
python -m summarize.services.llm_process
```

2. Optional: Limit the number of notes to summarize with top_k:

```bash
from summarize.services.llm_process import batch_summarize_and_save

# Summarize only top 5 notes
batch_summarize_and_save(top_k=5)
```

3. Output:

- Individual patient JSON files are saved in summarize/summaries/.

- A master index JSON file is also generated in the same folder.

## JSON Output Structure

Each patient summary JSON file has this structure:

```bash
{
  "record_id": 1,
  "processed_at": "2025-09-28T10:15:00",
  "original_text_length": 1234,
  "summary": {
    "Patient": "John Doe, 45M",
    "Diagnosis": "Hypertension",
    "Treatment": "Lisinopril 10mg daily",
    "Follow-up": "Check blood pressure in 2 weeks"
  }
}
```

## Dependencies

- google-generativeai

- faiss-cpu

- numpy

- Standard libraries: os, re, json, datetime

- Make sure the FAISS index (document_embeddings.index) and stored texts (texts.npy) are present in document_ai/faiss/ before running this script.

## License

This project is licensed under the MIT License.

