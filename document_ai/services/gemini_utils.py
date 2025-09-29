import os
import google.generativeai as genai
from config.settings import GOOGLE_API_KEY

genai.api_key = GOOGLE_API_KEY

def generate_answer(prompt: str, model: str = "gemini-1.5") -> str:
    """
    Call Gemini API with the prompt and return the answer.
    """
    try:
        response = genai.chat.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.last
    except Exception as e:
        return f"Error generating answer: {str(e)}"
