from typing import Dict, List, Optional
import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from prompter_core import build_prompt, normalize_list, VALID_CATEGORIES

# --- Optional: Google Gemini integration ---
_GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai  # type: ignore
    if os.getenv("GOOGLE_API_KEY"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        _GEMINI_AVAILABLE = True
except Exception:
    _GEMINI_AVAILABLE = False

# --- SQLite for newsletter ---
from sqlalchemy import Column, DateTime, Integer, String, create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = os.getenv("DATABASE_URL", "sqlite:///newsletter.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


class PromptRequest(BaseModel):
    category: str = Field(..., description="One of Content Writing | Design | Code | Image Generation")
    idea: str = Field(..., description="Initial idea in plain words")
    role: Optional[str] = Field(None, description="Optional role context")
    sources: List[str] = Field(default_factory=list)
    image: Optional[str] = None
    tones: List[str] = Field(default_factory=list)
    output_length: Optional[str] = None
    output_format: Optional[str] = None
    extras: List[str] = Field(default_factory=list)
    temperature: Optional[float] = Field(None, description="Creativity scale 0.0-1.0")
    media_resolution: Optional[str] = Field(None, description="low | medium | high")
    model: Optional[str] = Field(None, description="Target model hint")
    provider: Optional[str] = Field(None, description="ChatGPT | Grok | Perplexity | Gemini | MiniMax")


class PromptResponse(BaseModel):
    prompt: str


app = FastAPI(title="Master Prompter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/optimize", response_model=PromptResponse)
def optimize(req: PromptRequest) -> PromptResponse:
    if req.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")

    sources = normalize_list(req.sources)
    tones = normalize_list(req.tones)
    extras = normalize_list(req.extras)

    prompt = build_prompt(
        category=req.category,
        idea=req.idea,
        role=req.role,
        sources=sources,
        image=req.image,
        tones=tones,
        output_length=req.output_length,
        output_format=req.output_format,
        extras=extras,
        temperature=req.temperature,
        media_resolution=req.media_resolution,
        model=req.model,
        provider=req.provider,
    )
    return PromptResponse(prompt=prompt)


class TokenRequest(BaseModel):
    text: str
    model: Optional[str] = None


class TokenResponse(BaseModel):
    tokens: int


@app.post("/tokens", response_model=TokenResponse)
def tokens(req: TokenRequest) -> TokenResponse:
    # Light-weight fallback token estimate if Gemini not configured
    # 1 token ~= 4 chars English heuristic
    text = (req.text or "").strip()
    estimate = max(0, int(len(text) / 4))
    return TokenResponse(tokens=estimate)


class SubscribeRequest(BaseModel):
    email: str


class SubscribeResponse(BaseModel):
    status: str


@app.post("/subscribe", response_model=SubscribeResponse)
def subscribe(req: SubscribeRequest) -> SubscribeResponse:
    email = (req.email or "").strip().lower()
    if not email or "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Invalid email")
    session = SessionLocal()
    try:
        sub = Subscriber(email=email)
        session.add(sub)
        session.commit()
        return SubscribeResponse(status="subscribed")
    except IntegrityError:
        session.rollback()
        return SubscribeResponse(status="already_subscribed")
    finally:
        session.close()


class EnhanceRequest(BaseModel):
    prompt: str
    model: Optional[str] = Field(None, description="Gemini model id, e.g., gemini-1.5-pro")
    temperature: Optional[float] = None


class EnhanceResponse(BaseModel):
    enhanced: str
    provider: str


@app.post("/enhance", response_model=EnhanceResponse)
def enhance(req: EnhanceRequest) -> EnhanceResponse:
    if not _GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini not configured. Set GOOGLE_API_KEY.")
    model_id = req.model or "gemini-1.5-pro"
    try:
        model = genai.GenerativeModel(model_id)
        generation_config = {}
        if req.temperature is not None:
            generation_config["temperature"] = req.temperature
        result = model.generate_content(
            [
                "You are a prompt engineer. Improve the following prompt for clarity, completeness, and usefulness. Return only the improved prompt without extra commentary.",
                req.prompt,
            ],
            generation_config=generation_config or None,
        )
        enhanced = (result.text or "").strip()
        return EnhanceResponse(enhanced=enhanced, provider="Gemini")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhance failed: {e}")


