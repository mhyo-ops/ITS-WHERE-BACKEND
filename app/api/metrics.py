from __future__ import annotations
import base64
import json
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db import models
from ..db.base import get_db

router = APIRouter(prefix="/metrics", tags=["Eco Metrics"])
security = HTTPBearer()


class EcoMetrics(BaseModel):
    total_queries: int
    cache_hits: int
    llm_calls: int
    cache_hit_rate_percent: float
    avg_response_time_ms: float
    avg_cached_response_time_ms: float
    avg_llm_response_time_ms: float
    estimated_energy_saved_wh: float
    queries_by_language: Dict[str, int]
    queries_by_wilaya: Dict[str, int]
    period: str = "all-time"


def _decode_jwt_payload(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        payload_segment = parts[1]
        padded = payload_segment + "=" * ((4 - len(payload_segment) % 4) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded)
        payload = json.loads(decoded_bytes.decode("utf-8"))
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token") from exc


def _require_superadmin(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
) -> None:
    token = credentials.credentials
    payload = _decode_jwt_payload(token)
    admin_slug = payload.get("admin_slug") or payload.get("sub")
    if not admin_slug:
        raise HTTPException(status_code=401, detail="Invalid token: missing admin_slug")
    
    admin = db.query(models.AdminUser).filter(models.AdminUser.admin_slug == admin_slug).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/", response_model=EcoMetrics)
def get_metrics(db: Session = Depends(get_db)) -> EcoMetrics:
    total_queries = db.query(func.count(models.QueryLog.id)).scalar() or 0
    cache_hits = (
        db.query(func.count(models.QueryLog.id))
        .filter(models.QueryLog.cache_hit.is_(True))
        .scalar()
        or 0
    )
    llm_calls = total_queries - cache_hits

    avg_response_time = db.query(func.avg(models.QueryLog.response_time_ms)).scalar() or 0.0
    avg_cached_response_time = (
        db.query(func.avg(models.QueryLog.response_time_ms))
        .filter(models.QueryLog.cache_hit.is_(True))
        .scalar()
        or 0.0
    )
    avg_llm_response_time = (
        db.query(func.avg(models.QueryLog.response_time_ms))
        .filter(models.QueryLog.cache_hit.is_(False))
        .scalar()
        or 0.0
    )

    language_rows = (
        db.query(models.QueryLog.language, func.count(models.QueryLog.id))
        .filter(models.QueryLog.language.isnot(None))
        .group_by(models.QueryLog.language)
        .all()
    )
    wilaya_rows = (
        db.query(models.QueryLog.wilaya_filter, func.count(models.QueryLog.id))
        .filter(models.QueryLog.wilaya_filter.isnot(None))
        .group_by(models.QueryLog.wilaya_filter)
        .all()
    )

    queries_by_language = {language: count for language, count in language_rows}
    queries_by_wilaya = {wilaya: count for wilaya, count in wilaya_rows}

    cache_hit_rate = 0.0
    if total_queries > 0:
        cache_hit_rate = (cache_hits / total_queries) * 100.0

    return EcoMetrics(
        total_queries=total_queries,
        cache_hits=cache_hits,
        llm_calls=llm_calls,
        cache_hit_rate_percent=round(cache_hit_rate, 2),
        avg_response_time_ms=round(float(avg_response_time), 2),
        avg_cached_response_time_ms=round(float(avg_cached_response_time), 2),
        avg_llm_response_time_ms=round(float(avg_llm_response_time), 2),
        estimated_energy_saved_wh=round(float(cache_hits) * settings.ENERGY_PER_LLM_CALL_WH, 4),
        queries_by_language=queries_by_language,
        queries_by_wilaya=queries_by_wilaya,
        period="all-time",
    )


@router.get("/reset")
def reset_metrics(
    db: Session = Depends(get_db),
    _: None = Depends(_require_superadmin),
) -> dict:
    deleted = db.query(models.QueryLog).delete()
    db.commit()
    return {"message": "QueryLog cleared", "deleted": deleted}
