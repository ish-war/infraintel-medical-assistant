import os
import faiss
import numpy as np
import json
import google.generativeai as genai
from config.settings import GOOGLE_API_KEY
from datetime import datetime
import re 

# ----------------- Configure Gemini -----------------
genai.configure(api_key=GOOGLE_API_KEY)
GEMINI_MODEL = "gemini-2.5-flash"  # or gemini-1.5-pro if needed

# ----------------- Load FAISS and Texts -----------------
FAISS_INDEX_FILE = os.path.join("document_ai", "faiss", "document_embeddings.index")
TEXTS_FILE = os.path.join("document_ai", "faiss", "texts.npy")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARIES_DIR = os.path.join(BASE_DIR, "..", "summaries")

# Create summaries directory if it doesn't exist
os.makedirs(SUMMARIES_DIR, exist_ok=True)

# Load stored texts
if os.path.exists(TEXTS_FILE):
    stored_texts = np.load(TEXTS_FILE, allow_pickle=True).tolist()
else:
    stored_texts = []

# Load FAISS index (already built in Task 1)
if os.path.exists(FAISS_INDEX_FILE):
    faiss_index = faiss.read_index(FAISS_INDEX_FILE)
    print("✅ Loaded FAISS index for LLM summarization.")
else:
    faiss_index = None
    print("⚠️ FAISS index not found. Run Task 1 first to build it.")


# ----------------- Functions -----------------
def retrieve_notes(top_k: int = None):
    """
    Retrieve notes from stored_texts.
    If top_k is None, retrieve all notes.
    """
    if not stored_texts:
        print("⚠️ No stored_texts found.")
        return []

    if top_k is None or top_k > len(stored_texts):
        return stored_texts
    else:
        return stored_texts[:top_k]


def create_enhanced_prompt(note_text: str) -> str:
    """Create an enhanced prompt for clinical note summarization."""
    prompt = f"""
You are a medical professional assistant. Please analyze the following clinical text and extract key information into a structured JSON format.

Clinical Text:
{note_text}

Please provide a JSON response with EXACTLY the following structure:
{{
    "Patient": "Patient identifier or demographic info (age, gender if mentioned)",
    "Diagnosis": "Primary diagnosis or medical condition identified",
    "Treatment": "Treatment plan, medications, or procedures mentioned",
    "Follow-up": "Follow-up instructions, next appointments, or monitoring plans"
}}

Important guidelines:
- Extract only information explicitly mentioned in the text
- Use "Not specified" if information is not available
- Keep responses concise and factual
- Focus on medical relevance
- Do not include any text outside the JSON format
- Ensure all field names match exactly as shown above

Respond ONLY with valid JSON, no extra text, no explanation, no markdown formatting.
"""
    return prompt


def generate_patient_filename(summary: dict, record_id: int) -> str:
    """Generate a unique filename for each patient summary."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Try to extract patient info for filename
    patient_info = summary.get("Patient", "Unknown")
    
    # Clean patient info for filename (remove special characters)
    clean_patient = re.sub(r'[^\w\s-]', '', str(patient_info))
    clean_patient = re.sub(r'[-\s]+', '_', clean_patient)
    
    # Limit filename length
    if len(clean_patient) > 30:
        clean_patient = clean_patient[:30]
    
    # Create filename
    filename = f"patient_{record_id:03d}_{clean_patient}_{timestamp}.json"
    
    return filename


def save_patient_summary(summary: dict, record_id: int, original_text: str) -> str:
    """Save or update individual patient summary to a JSON file."""
    try:
        # Add metadata to summary
        enhanced_summary = {
            "record_id": record_id,
            "processed_at": datetime.now().isoformat(),
            "original_text_length": len(original_text),
            "summary": summary,
            
        }

        # Clean patient info for filename
        patient_info = summary.get("Patient", "Unknown")
        clean_patient = re.sub(r'[^\w\s-]', '', str(patient_info))
        clean_patient = re.sub(r'[-\s]+', '_', clean_patient)
        if len(clean_patient) > 30:
            clean_patient = clean_patient[:30]

        # Check if a file already exists for this patient
        existing_files = [
            f for f in os.listdir(SUMMARIES_DIR)
            if f.startswith(f"patient_{clean_patient}_") and f.endswith(".json")
        ]

        if existing_files:
            # Overwrite the first matching file
            filepath = os.path.join(SUMMARIES_DIR, existing_files[0])
            print(f"🔄 Updating existing summary for patient: {clean_patient}")
        else:
            # Create a new file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"patient_{clean_patient}.json"
            filepath = os.path.join(SUMMARIES_DIR, filename)

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(enhanced_summary, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved summary for patient {clean_patient}: {os.path.basename(filepath)}")
        return filepath

    except Exception as e:
        print(f"❌ Error saving summary for record {record_id}: {e}")
        return None



# ----------------- Gemini Summarization -----------------
def summarize_note_with_gemini(note_text: str):
    """
    Send note text to Gemini for structured summarization.
    Expected output: JSON with fields Patient, Diagnosis, Treatment, Follow-up.
    """
    try:
        # Use the enhanced prompt
        prompt = create_enhanced_prompt(note_text)
        
        response = genai.GenerativeModel(GEMINI_MODEL).generate_content(prompt)
        raw_text = response.text.strip()
        
        # Remove any markdown formatting
        raw_text = re.sub(r'```json\s*', '', raw_text)
        raw_text = re.sub(r'```\s*', '', raw_text)
        
        # Extract JSON part if Gemini adds extra formatting
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            raw_text = match.group(0)

        summary = json.loads(raw_text)
        
        # Validate that all required fields are present
        required_fields = ["Patient", "Diagnosis", "Treatment", "Follow-up"]
        for field in required_fields:
            if field not in summary:
                summary[field] = "Not specified"
        
        return summary

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Raw response: {raw_text}")
        # Return fallback structure
        return {
            "Patient": "Error in processing",
            "Diagnosis": "Error in processing", 
            "Treatment": "Error in processing",
            "Follow-up": "Error in processing",
            "error": f"JSON parsing failed: {str(e)}",
            "raw_response": raw_text
        }
    except Exception as e:
        print(f"❌ Error generating summary with Gemini: {e}")
        return {
            "Patient": "Error in processing",
            "Diagnosis": "Error in processing",
            "Treatment": "Error in processing", 
            "Follow-up": "Error in processing",
            "error": str(e)
        }


def batch_summarize_and_save(top_k: int = 3):
    """Retrieve top_k notes, summarize each note, and save to separate files."""
    notes = retrieve_notes(top_k)
    summaries = []
    saved_files = []
    
    print(f"Processing {len(notes)} clinical notes...")
    
    for i, note in enumerate(notes):
        print(f"\nProcessing record {i+1}/{len(notes)}...")
        
        # Skip very short notes
        if len(str(note).strip()) < 50:
            print(f"⚠️ Skipping record {i+1}: Note too short")
            continue
        
        # Generate summary
        summary = summarize_note_with_gemini(str(note))
        summaries.append(summary)
        
        # Save to individual file
        filepath = save_patient_summary(summary, i+1, str(note))
        if filepath:
            saved_files.append(filepath)
        
        print(f"Summary preview: {summary.get('Patient', 'N/A')} - {summary.get('Diagnosis', 'N/A')}")
    
    # Create a master index file
    master_index = {
        "total_records": len(summaries),
        "processed_at": datetime.now().isoformat(),
        "files": saved_files,
        "summary_preview": summaries
    }
    
    master_file = os.path.join(SUMMARIES_DIR, f"master_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Processing complete!")
    print(f"📁 {len(saved_files)} individual patient files saved")
    print(f"📋 Master index saved: {master_file}")
    
    return summaries, saved_files


def batch_summarize(top_k: int = 3):
    """Original function maintained for backward compatibility."""
    notes = retrieve_notes(top_k)
    summaries = []
    for note in notes:
        summary = summarize_note_with_gemini(note)
        summaries.append(summary)
    return summaries


if __name__ == "__main__":
    # Test with enhanced functionality
    print("=" * 50)
    print("Clinical Record Summarization Tool")
    print("=" * 50)
    
    # Process and save summaries
    results, files = batch_summarize_and_save(top_k=None)
    
    print("\nSample Summary:")
    if results:
        print(json.dumps(results[0], indent=2))