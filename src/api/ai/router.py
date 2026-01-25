"""
AI Gateway router - proxy to AI providers with token management.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from ..core.config import settings
from ..core.database import get_db
from ..models.user import User
from ..models.project import Project, AISession
from ..auth.router import get_current_user

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    project_id: int
    messages: List[Message]
    model: Optional[str] = None
    stream: bool = False
    max_tokens: int = 4096


class ChatResponse(BaseModel):
    id: str
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    input_price: float
    output_price: float


AVAILABLE_MODELS = [
    ModelInfo(id="claude-sonnet-4-20250514", name="Claude Sonnet 4", provider="anthropic", input_price=3.0, output_price=15.0),
    ModelInfo(id="claude-3-5-haiku-20241022", name="Claude 3.5 Haiku", provider="anthropic", input_price=0.8, output_price=4.0),
    ModelInfo(id="gpt-4o", name="GPT-4o", provider="openai", input_price=2.5, output_price=10.0),
    ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", provider="openai", input_price=0.15, output_price=0.6),
]


async def call_anthropic(messages: List[dict], model: str, max_tokens: int, system: str = None) -> dict:
    async with httpx.AsyncClient() as client:
        payload = {"model": model, "max_tokens": max_tokens, "messages": messages}
        if system:
            payload["system"] = system
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            json=payload,
            headers={"x-api-key": settings.ANTHROPIC_API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01"},
            timeout=120.0,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"API error: {response.text}")
        data = response.json()
        return {
            "id": data.get("id", ""),
            "content": data["content"][0]["text"] if data.get("content") else "",
            "input_tokens": data.get("usage", {}).get("input_tokens", 0),
            "output_tokens": data.get("usage", {}).get("output_tokens", 0),
        }


@router.get("/models", response_model=List[ModelInfo])
async def list_models():
    return AVAILABLE_MODELS


@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.tokens_balance <= 0:
        raise HTTPException(status_code=402, detail="Insufficient tokens")
    
    result = await db.execute(select(Project).where(Project.id == data.project_id).where(Project.owner_id == current_user.id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    model = data.model or settings.DEFAULT_AI_MODEL
    model_info = next((m for m in AVAILABLE_MODELS if m.id == model), None)
    if not model_info:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model}")
    
    messages = [{"role": m.role, "content": m.content} for m in data.messages]
    system_prompt = f"Project: {project.name}\nType: {project.type.value}\n{project.context_summary or ''}"
    
    result = await call_anthropic(messages=messages, model=model, max_tokens=data.max_tokens, system=system_prompt)
    
    total_tokens = result["input_tokens"] + result["output_tokens"]
    current_user.tokens_balance -= total_tokens
    
    session = AISession(
        project_id=project.id, user_id=current_user.id, model=model,
        input_tokens=result["input_tokens"], output_tokens=result["output_tokens"], total_tokens=total_tokens,
    )
    db.add(session)
    await db.flush()
    
    return ChatResponse(
        id=result["id"], content=result["content"], model=model,
        input_tokens=result["input_tokens"], output_tokens=result["output_tokens"], total_tokens=total_tokens,
    )