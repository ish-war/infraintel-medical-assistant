# Base image
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Copy requirements first (caching step)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY rag_agent/ ./rag_agent/
COPY config/ ./config/
COPY document_ai/ ./document_ai/
COPY summarize/ ./summarize/
COPY .env .
COPY main.py .

# Expose FastAPI port
EXPOSE 8000

# Run rag_agent service by default
CMD ["uvicorn", "rag_agent.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
