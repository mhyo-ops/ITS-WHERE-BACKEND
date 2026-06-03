from __future__ import annotations
from typing import List
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from ..cache.cache_ops import (
    get_cached,
    invalidate_discover_cache,
    invalidate_event_list_cache,
    make_event_detail_key,
    make_event_list_key,
    set_cached,
)
from ..cache.redis_client import get_redis
from ..core.dependencies import get_current_admin, get_db
from ..core.language import get_preferred_language, localize_event, localize_event_list
from ..crud.event import (
    create_event,
    deactivate_event,
    get_event,
    get_events,
    update_event,
)
from ..schemas.event import EventCreate, EventRead, EventUpdate
from ..schemas.event_slim import EventSlim

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=List[EventSlim], response_class=JSONResponse)
async def list_events(
    skip: int = 0,
    limit: int = 100,
    wilaya: str | None = Query(None),
    postal_code: str | None = Query(None),
    category_id: int | None = Query(None),
    status: str | None = Query(None),
    lang: str | None = Query(None),
    active_only: bool = True,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> JSONResponse:
    preferred_lang = get_preferred_language(lang)
    key = make_event_list_key(wilaya, postal_code, category_id, status, skip, limit, preferred_lang)
    cached = await get_cached(redis, key)
    if cached:
        return JSONResponse(content=json.loads(cached), headers={"X-Cache": "HIT"})

    events = get_events(
        db,
        skip=skip,
        limit=limit,
        wilaya=wilaya,
        postal_code=postal_code,
        category_id=category_id,
        status=status,
        active_only=active_only,
        slim=True,
    )
    payload = [EventSlim.model_validate(event).model_dump(exclude_none=True) for event in events]
    json_payload = jsonable_encoder(payload)
    localized_payload = localize_event_list(json_payload, preferred_lang)
    await set_cached(redis, key, json.dumps(localized_payload, default=str), ttl_seconds=600)
    return JSONResponse(content=localized_payload, headers={"X-Cache": "MISS"})


@router.get("/{event_id}", response_model=EventRead, response_class=JSONResponse)
async def read_event(
    event_id: int,
    lang: str | None = Query(None),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> JSONResponse:
    preferred_lang = get_preferred_language(lang)
    key = make_event_detail_key(event_id, preferred_lang)
    cached = await get_cached(redis, key)
    if cached:
        return JSONResponse(content=json.loads(cached), headers={"X-Cache": "HIT"})

    event = get_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    payload = EventRead.model_validate(event).model_dump(exclude_none=True)
    localized_payload = localize_event(payload, preferred_lang)
    await set_cached(redis, key, json.dumps(localized_payload, default=str), ttl_seconds=1800)
    return JSONResponse(content=localized_payload, headers={"X-Cache": "MISS"})


@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event_endpoint(
    data: EventCreate,
    _: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> EventRead:
    event = create_event(db, data)
    await invalidate_event_list_cache(redis)
    await invalidate_discover_cache(redis)
    return event


@router.put("/{event_id}", response_model=EventRead)
async def update_event_endpoint(
    event_id: int,
    data: EventUpdate,
    _: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> EventRead:
    event = update_event(db, event_id, data)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    await invalidate_event_list_cache(redis)
    await invalidate_discover_cache(redis)
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    _: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    event = deactivate_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    await invalidate_event_list_cache(redis)
    await invalidate_discover_cache(redis)
    return {"message": "Event deactivated", "id": event_id}
