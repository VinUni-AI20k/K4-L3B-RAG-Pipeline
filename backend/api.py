"""
backend/api.py — FastAPI bridge giữa React frontend và Python RAG pipeline.

Chay:
    uvicorn backend.api:app --reload --port 8000

Endpoints:
    POST /generate  → GenerationResult
    POST /retrieve  → list[SearchResult]
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Thêm project root vào path để import src.*
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
load_dotenv()

app = FastAPI(title="TravelBot RAG API", version="1.0.0")

# CORS — cho phép React dev server (port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Request / Response schemas
# ─────────────────────────────────────────────

class GenerateRequest(BaseModel):
    query:    str
    top_k:    int    = 5
    provider: str    = "openai"
    model:    str    = ""
    threshold: float = 0.45


class RetrieveRequest(BaseModel):
    query:  str
    top_k:  int = 5
    method: str = "hybrid"   # "dense" | "bm25" | "hybrid" | "pageindex"


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
async def generate(req: GenerateRequest):
    """Gọi generate_with_citation và trả GenerationResult."""
    # Sync provider/model vào env cho task10 đọc
    os.environ["LLM_PROVIDER"] = req.provider
    if req.model:
        os.environ["LLM_MODEL"] = req.model
    os.environ["SCORE_THRESHOLD"] = str(req.threshold)

    try:
        from src.task10_generation import generate_with_citation  # noqa: PLC0415
        result = generate_with_citation(req.query, top_k=req.top_k)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/retrieve")
async def retrieve(req: RetrieveRequest):
    """Gọi retrieve hoặc pageindex_search, dùng cho A/B compare."""
    try:
        if req.method == "pageindex":
            from src.task8_pageindex_vectorless import pageindex_search  # noqa: PLC0415
            chunks = pageindex_search(req.query, top_k=req.top_k)
        elif req.method == "dense":
            from src.task5_semantic_search import semantic_search  # noqa: PLC0415
            chunks = semantic_search(req.query, top_k=req.top_k)
        elif req.method == "bm25":
            from src.task6_lexical_search import lexical_search  # noqa: PLC0415
            chunks = lexical_search(req.query, top_k=req.top_k)
        else:
            from src.task9_retrieval_pipeline import retrieve as _retrieve  # noqa: PLC0415
            chunks = _retrieve(req.query, top_k=req.top_k, use_reranking=True)
        return {"chunks": chunks}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
