# rag_agent/api/fastapi_app.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rag_agent.services.llm_agent import answer_query

# Initialize FastAPI app
app = FastAPI(title="RAG Medical Assistant", version="1.0")

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="rag_agent/static"), name="static")

# Templates
templates = Jinja2Templates(directory="rag_agent/templates")


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    use_gemini: bool = True


# --------- UI ROUTES ---------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask-ui", response_class=HTMLResponse)
def ask_ui(request: Request, question: str = Form(...), use_gemini: bool = Form(True)):
    # Determine top_k dynamically (optional: parse query for number)
    top_k = None  # None means fetch all summaries

    result = answer_query(question=question, top_k=top_k, use_gemini=use_gemini)

    return templates.TemplateResponse("results.html", {
        "request": request,
        "question": question,
        "result": result
    })


# --------- API ROUTES (unchanged) ---------
@app.get("/api")
def api_status():
    return {"message": "RAG Medical Assistant API is running 🚀"}

@app.post("/ask")
def ask_question(request: QueryRequest):
    result = answer_query(
        question=request.question,
        top_k=request.top_k,
        use_gemini=request.use_gemini
    )
    return result
