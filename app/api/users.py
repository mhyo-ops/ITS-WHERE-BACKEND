from __future__ import annotations
from typing import List
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from ..cache.cache_ops import get_cached, make_discover_key, set_cached
from ..core.language import get_preferred_language, localize_event_list
from ..cache.redis_client import get_redis
from ..core.dependencies import get_current_user, get_db
from ..crud import user as crud_user
from ..crud.event import get_events_filtered
from ..schemas.category import CategoryRead
from ..schemas.event_slim import EventSlim
from ..schemas.event import EventRead
from ..schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    user = crud_user.get_user(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/me", response_model=UserRead)
def update_current_user(
    data: UserUpdate,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    user = crud_user.update_user(db, current_user.id, data)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/me")
def deactivate_current_user(
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user = crud_user.deactivate_user(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "Account deactivated"}


@router.get("/me/favourites", response_model=List[CategoryRead])
def get_favourite_categories(
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[CategoryRead]:
    user = crud_user.get_user(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user.favourite_categories


@router.post("/me/favourites/{category_id}")
def add_favourite_category(
    category_id: int,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    crud_user.add_favourite_category(db, current_user.id, category_id)
    return {"message": "Category added to favourites"}


@router.delete("/me/favourites/{category_id}")
def remove_favourite_category(
    category_id: int,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    crud_user.remove_favourite_category(db, current_user.id, category_id)
    return {"message": "Category removed from favourites"}


@router.get("/me/events/discover/wilaya", response_model=List[EventSlim], response_class=JSONResponse)
async def discover_events_by_wilaya(
    wilaya: str = Query(...),
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> JSONResponse:
    fav_ids = [c.id for c in current_user.favourite_categories]
    preferred_lang = get_preferred_language(current_user.preferred_language)
    key = make_discover_key("wilaya", wilaya, fav_ids, status, skip, limit, preferred_lang)
    cached = await get_cached(redis, key)
    if cached:
        return JSONResponse(content=json.loads(cached), headers={"X-Cache": "HIT"})

    category_ids = fav_ids if fav_ids else None
    events = get_events_filtered(
        db,
        wilaya=wilaya,
        category_ids=category_ids,
        status=status,
        skip=skip,
        limit=limit,
    )
    payload = [EventSlim.model_validate(event).model_dump(exclude_none=True) for event in events]
    json_payload = jsonable_encoder(payload)
    localized_payload = localize_event_list(json_payload, preferred_lang)
    await set_cached(redis, key, json.dumps(localized_payload, default=str), ttl_seconds=300)
    return JSONResponse(content=localized_payload, headers={"X-Cache": "MISS"})


@router.get("/me/events/discover/commune", response_model=List[EventSlim], response_class=JSONResponse)
async def discover_events_by_commune(
    commune: str = Query(...),
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> JSONResponse:
    fav_ids = [c.id for c in current_user.favourite_categories]
    preferred_lang = get_preferred_language(current_user.preferred_language)
    key = make_discover_key("commune", commune, fav_ids, status, skip, limit, preferred_lang)
    cached = await get_cached(redis, key)
    if cached:
        return JSONResponse(content=json.loads(cached), headers={"X-Cache": "HIT"})

    category_ids = fav_ids if fav_ids else None
    events = get_events_filtered(
        db,
        commune=commune,
        category_ids=category_ids,
        status=status,
        skip=skip,
        limit=limit,
    )
    payload = [EventSlim.model_validate(event).model_dump(exclude_none=True) for event in events]
    json_payload = jsonable_encoder(payload)
    localized_payload = localize_event_list(json_payload, preferred_lang)
    await set_cached(redis, key, json.dumps(localized_payload, default=str), ttl_seconds=300)
    return JSONResponse(content=localized_payload, headers={"X-Cache": "MISS"})


@router.get("/me/events", response_model=List[EventRead])
def list_registered_events(
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[EventRead]:
    user = crud_user.get_user(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user.registered_events


@router.post("/me/events/{event_id}")
def register_for_event(
    event_id: int,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    crud_user.register_event(db, current_user.id, event_id)
    return {"message": "Successfully registered for event"}


@router.delete("/me/events/{event_id}")
def unregister_from_event(
    event_id: int,
    current_user: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    crud_user.unregister_event(db, current_user.id, event_id)
    return {"message": "Successfully unregistered from event"}
