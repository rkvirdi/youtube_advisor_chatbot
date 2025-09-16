# src/ask.py
from dotenv import load_dotenv
load_dotenv()  # IMPORTANT: do this before importing generator so GROQ_API_KEY is visible

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.utils.retriever import retrieve_relevant_chunks
from src.utils.generator import generate_response

app = FastAPI(title="YouTube Advisor API", version="1.0.0")

# Optional CORS (adjust for your frontend origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with ["http://localhost:3000"] for stricter policy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    k: int = Field(30, ge=1, le=100, description="how many candidates to pull from Weaviate")
    alpha: float = Field(0.15, ge=0.0, le=1.0, description="BM25 vs vector blend (lower = more semantic)")

class AskResponse(BaseModel):
    answer: str
    retrieved: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    q = req.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Read-only retrieval (computes ONLY the query embedding)
    chunks = retrieve_relevant_chunks(q, top_k=req.k, alpha=req.alpha)

    # Generate summarized answer with citations (Groq if GROQ_API_KEY is set, else extractive fallback)
    answer = generate_response(q, chunks)

    return AskResponse(answer=answer, retrieved=len(chunks))
