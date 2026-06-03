from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter
from pydantic import BaseModel

from app.cache.redis_client import get_redis
from app.core.chatbot import chat

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    lang: str = "fr"


class ChatResponse(BaseModel):
    answer: str
    matched_event_ids: list[int]
    events_used: int
    cached: bool = False


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    RAG chatbot endpoint.
    Accepts natural language in FR/AR/TZM.
    Returns answer + matched events.
    Redis cached for 1800s per unique message.
    """
    redis = await get_redis()

    # Cache key based on message hash
    cache_key = f"chat:{hashlib.md5(request.message.lower().strip().encode()).hexdigest()}"

    # Check cache
    cached = await redis.get(cache_key)
    if cached:
        result = json.loads(cached)
        result["cached"] = True
        return ChatResponse(**result)

    # Run RAG pipeline
    result = await chat(request.message, request.lang)
    result["cached"] = False

    # Cache result
    await redis.setex(cache_key, 1800, json.dumps(result))

    return ChatResponse(**result)
