# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from recommender import get_recommendations
import requests
from readability import Document
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SHL Assessment Recommender")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    query: str | None = None
    url: HttpUrl | None = None
    max_recs: int = 5
    use_llm_rerank: bool = False

class RecommendationItem(BaseModel):
    assessment_name: str
    url: HttpUrl
    short_reason: str | None = None
    relevance_score: float

class RecommendResponse(BaseModel):
    recommendations: list[RecommendationItem]

@app.get("/health")
def health():
    return {"status": "healthy"}

def fetch_text_from_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        doc = Document(r.text)
        summary = doc.summary()  # HTML snippet
        # Strip tags
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(summary, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

@app.post("/recommend")
def recommend(req: RecommendRequest):
    print(f"🔑 OPENAI key detected in environment? {bool(os.getenv('OPENAI_API_KEY'))}")
    if not req.query and not req.url:
        raise HTTPException(status_code=400, detail="Provide either 'query' or 'url'.")
    
    text = req.query or ""
    if req.url:
        text = fetch_text_from_url(str(req.url))
    
    max_recs = 10
    
    try:
        recs = get_recommendations(text, max_recs=max_recs, use_llm=True)
        # Format output exactly as required
        out = []
        for r in recs:
            out.append({
                "url": r.get("url"),
                "assessment_name": r.get("assessment_name"),
                "adaptive_support": r.get("adaptive_support", "No"),
                "description": r.get("jd", ""),
                "duration": r.get("duration", ""),
                "remote_support": r.get("remote_support", "No"),
                "test_type": r.get("test_type", []),
            })
        return {"recommended_assessments": out}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
