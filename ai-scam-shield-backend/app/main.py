from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from typing import Optional, List

from .core import analyze_text as core_analyze_text, recovery_analysis as core_recovery_analysis


app = FastAPI(title="AI Scam & Fraud Shield - Backend")

# CORS: allow local frontend dev servers (Vite default + common local hosts)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
REPORTS_PATH = os.path.join(BASE_DIR, "reports.json")

# Ensure reports.json exists
if not os.path.exists(REPORTS_PATH):
    with open(REPORTS_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)


class AnalyzeRequest(BaseModel):
    text: str
    source_type: Optional[str] = "message"


class AnalyzeResponse(BaseModel):
    trust_score: float
    heuristic_score: float
    model_score: Optional[float]
    reasons: List[str]
    recommended_action: str


@app.post("/analyze")
def analyze(payload: dict):
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    return core_analyze_text(text)


@app.post("/recovery")
def recovery(payload: dict):
    conversation_text = payload.get("conversation_text")
    if not conversation_text:
        raise HTTPException(status_code=400, detail="conversation_text is required")
    return core_recovery_analysis(conversation_text)


@app.post("/report")
def report(payload: dict):
    with open(REPORTS_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(payload)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    return {"status": "ok", "saved": True}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import json
import os
from typing import List, Optional

app = FastAPI(title="AI Scam & Fraud Shield - Backend")
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from typing import Optional, List

from .core import analyze_text as core_analyze_text, recovery_analysis as core_recovery_analysis


app = FastAPI(title="AI Scam & Fraud Shield - Backend")

# CORS: allow local frontend dev servers (Vite default + common local hosts)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
REPORTS_PATH = os.path.join(BASE_DIR, "reports.json")

# Ensure reports.json exists
if not os.path.exists(REPORTS_PATH):
    with open(REPORTS_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)


class AnalyzeRequest(BaseModel):
    text: str
    source_type: Optional[str] = "message"


class AnalyzeResponse(BaseModel):
    trust_score: float
    heuristic_score: float
    model_score: Optional[float]
    reasons: List[str]
    recommended_action: str


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    return core_analyze_text(req.text)


@app.post("/recovery")
def recovery(payload: dict):
    conversation_text = payload.get("conversation_text")
    if not conversation_text:
        raise HTTPException(status_code=400, detail="conversation_text is required")
    return core_recovery_analysis(conversation_text)


@app.post("/report")
def report(payload: dict):
    with open(REPORTS_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(payload)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    return {"status": "ok", "saved": True}

