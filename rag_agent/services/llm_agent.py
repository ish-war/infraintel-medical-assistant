# rag_agent/services/llm_agent.py
import json
from typing import List, Dict, Any, Optional

from config.settings import GOOGLE_API_KEY
import google.generativeai as genai

from .rag_utils import load_summary_index, search_summary_index

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
GEMINI_MODEL = "gemini-2.5-flash"  # desired model

def generate_answer_with_gemini(question: str, context_text: str, model: str = GEMINI_MODEL) -> str:
    """
    Sends a prompt to Gemini and returns text result.
    If you don't want to use Gemini, you can skip calling this and just return metadata.
    """
    prompt = (
        "You are a medical assistant. Use the context below (structured patient summaries) to answer the question.\n\n"
        f"Context:\n{context_text}\n\nQuestion: {question}\n\nAnswer concisely and in plain text."
    )
    try:
        resp = genai.GenerativeModel(model).generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return f"Error generating answer: {e}"


def answer_query(
    question: str,
    top_k: Optional[int] = None,  # None = fetch all summaries
    use_gemini: bool = False,
) -> Dict[str, Any]:
    """
    1) Load summary index
    2) Retrieve top_k summary records (all if top_k=None)
    3) Optionally call Gemini to synthesize an answer
    4) Return only summaries that contributed to the answer and exclude NA/empty fields
    """
    index, texts, metadata_list = load_summary_index()

    # Determine number of results to fetch
    search_top_k = top_k if top_k is not None else len(metadata_list)

    retrieved = search_summary_index(
        question,
        top_k=search_top_k,
        index=index,
        metadata_list=metadata_list
    )

    filtered_retrieved = []
    context_items = []

    for r in retrieved:
        summary = r["metadata"].get("summary", {})

        # Keep only fields that have valid data
        valid_fields = {k: v for k, v in summary.items() if v and v.strip().upper() != "NA"}
        if not valid_fields:
            continue  # skip records with no valid data

        filtered_retrieved.append(r)

        # Build context string for Gemini from valid fields
        context_items.append("\n".join([f"{k}: {v}" for k, v in valid_fields.items()]))

    context_text = "\n\n---\n\n".join(context_items) if context_items else ""

    result = {"retrieved": filtered_retrieved, "retrieved_count": len(filtered_retrieved)}

    if use_gemini and context_text:
        answer = generate_answer_with_gemini(question, context_text)
        result["answer"] = answer

    return result
