from __future__ import annotations
from typing import Any, Dict, List, Optional

from qdrant_client.models import FieldCondition, Filter, MatchValue

from .qdrant_client import get_client
from .embeddings import embed
from ..core.config import settings


def retrieve(
    query: str,
    wilaya: Optional[str] = None,
    category: Optional[str] = None,
    language: Optional[str] = None,
    n_results: int = 5,
) -> List[Dict[str, Any]]:
    vector = embed(query)

    conditions = [
        FieldCondition(key="is_active", match=MatchValue(value=True)),
    ]
    if wilaya:
        conditions.append(FieldCondition(key="wilaya", match=MatchValue(value=wilaya)))
    if category:
        conditions.append(FieldCondition(key="category", match=MatchValue(value=category)))
    if language:
        conditions.append(FieldCondition(key="language", match=MatchValue(value=language)))

    query_filter = Filter(must=conditions)

    results = get_client().search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=vector,
        query_filter=query_filter,
        limit=n_results,
        with_payload=True,
    )

    return [
        {
            "id": r.id,
            "score": r.score,
            "payload": r.payload,
            "document": _format_document(r.payload),
        }
        for r in results
    ]


def _format_document(payload: dict) -> str:
    if payload.get("type") == "center":
        return (
            f"Youth Center: {payload.get('name')}. "
            f"Wilaya: {payload.get('wilaya')}. "
            f"Languages: {payload.get('languages')}.")
    return (
        f"Program: {payload.get('title')}. "
        f"Category: {payload.get('category')}. "
        f"Wilaya: {payload.get('wilaya')}. "
        f"Language: {payload.get('language')}.")


def build_context(results: List[Dict[str, Any]]) -> str:
    if not results:
        return "No relevant information found."

    blocks = []
    for r in results:
        score = round(r["score"], 3)
        blocks.append(
            f"--- [{r['payload'].get('type')}] (relevance: {score}) ---\n{r['document']}"
        )
    return "\n\n".join(blocks)
