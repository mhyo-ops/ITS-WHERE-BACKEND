from __future__ import annotations
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.config import settings
from ..cache.cache_ops import make_cache_key, get_cached, set_cached
from ..db import SessionLocal, models
from ..rag.retriever import build_context, retrieve


def build_prompt(query: str, context: str, language: Optional[str] = None) -> str:
    prompt_lines = [
        "You are an assistant for ODEJ Algeria. Answer ONLY using the provided context. Do not invent programs or centers. "
        "If the context does not contain the answer, say so clearly.",
        "",
        "Context:",
        context,
        "",
        f"User query: {query}",
    ]

    if language == "ar":
        prompt_lines.append("Respond in Arabic.")
    elif language == "tzm":
        prompt_lines.append("Respond in Tamazight if possible, otherwise French.")
    else:
        prompt_lines.append("Respond in French.")

    return "\n".join(prompt_lines)


async def call_ollama(prompt: str, model: str = settings.OLLAMA_LLM_MODEL) -> str:
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}

    async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            raise HTTPException(status_code=503, detail="LLM service unavailable") from exc

    if not isinstance(data, dict) or "response" not in data:
        raise HTTPException(status_code=503, detail="Invalid response from Ollama")

    return str(data["response"])


def _log_query_sync(
    query_text: str,
    language: Optional[str],
    wilaya_filter: Optional[str],
    cache_hit: bool,
    response_time_ms: int,
) -> None:
    db = SessionLocal()
    try:
        log_entry = models.QueryLog(
            query_text=query_text,
            language=language,
            wilaya_filter=wilaya_filter,
            cache_hit=cache_hit,
            response_time_ms=response_time_ms,
        )
        db.add(log_entry)
        db.commit()
    finally:
        db.close()


async def _log_query(
    query_text: str,
    language: Optional[str],
    wilaya_filter: Optional[str],
    cache_hit: bool,
    response_time_ms: int,
) -> None:
    await asyncio.to_thread(
        _log_query_sync,
        query_text,
        language,
        wilaya_filter,
        cache_hit,
        response_time_ms,
    )


async def run_query(
    query: str,
    wilaya: Optional[str] = None,
    category: Optional[str] = None,
    language: Optional[str] = None,
    redis: Any = None,
    db: Session | None = None,
) -> Dict[str, Any]:
    if redis is None:
        raise ValueError("Redis client must be provided")
    if db is None:
        raise ValueError("Database session must be provided")

    key = make_cache_key(query, wilaya, category, language)
    start_time = datetime.utcnow()

    cached = await get_cached(redis, key)
    if cached is not None:
        response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        asyncio.create_task(
            _log_query(
                query_text=query,
                language=language,
                wilaya_filter=wilaya,
                cache_hit=True,
                response_time_ms=response_time_ms,
            )
        )
        return {"answer": cached, "cache_hit": True, "source": "redis"}

    results = retrieve(query, wilaya, category, language, n_results=5)
    if not results:
        return {"answer": "No relevant ODEJ programs found.", "cache_hit": False, "source": "llm"}

    context = build_context(results)
    prompt = build_prompt(query, context, language)
    response = await call_ollama(prompt)
    await set_cached(redis, key, response, ttl_seconds=3600)

    response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    asyncio.create_task(
        _log_query(
            query_text=query,
            language=language,
            wilaya_filter=wilaya,
            cache_hit=False,
            response_time_ms=response_time_ms,
        )
    )

    return {"answer": response, "cache_hit": False, "source": "llm"}
