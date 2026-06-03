from __future__ import annotations
from typing import Any, List, Optional

from sqlalchemy.orm import Session

from ..core.translation import translate_event_fields
from ..core.embeddings import build_event_text, embed_text, upsert_event_embedding
from ..db import models
from ..schemas.event import EventCreate, EventUpdate


def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def get_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    wilaya: str | None = None,
    postal_code: str | None = None,
    category_id: int | None = None,
    status: str | None = None,
    active_only: bool = True,
    slim: bool = True,
) -> List[Any]:
    query = db.query(models.Event)
    if slim:
        query = query.with_entities(
            models.Event.id,
            models.Event.title,
            models.Event.title_ar,
            models.Event.title_fr,
            models.Event.title_tam,
            models.Event.wilaya,
            models.Event.commune,
            models.Event.postal_code,
            models.Event.date_begin,
            models.Event.date_end,
            models.Event.category_id,
            models.Event.status,
            models.Event.cost,
            models.Event.remaining_spots,
            models.Event.registration_required,
            models.Event.is_volunteering,
        )

    if active_only:
        query = query.filter(models.Event.is_active.is_(True))
    if wilaya is not None:
        query = query.filter(models.Event.wilaya == wilaya)
    if postal_code is not None:
        query = query.filter(models.Event.postal_code == postal_code)
    if category_id is not None:
        query = query.filter(models.Event.category_id == category_id)
    if status is not None:
        query = query.filter(models.Event.status == status)
    return query.offset(skip).limit(limit).all()


def get_events_filtered(
    db: Session,
    wilaya: str | None = None,
    commune: str | None = None,
    category_ids: list[int] | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Any]:
    query = db.query(models.Event).with_entities(
        models.Event.id,
        models.Event.title,
        models.Event.title_ar,
        models.Event.title_fr,
        models.Event.title_tam,
        models.Event.wilaya,
        models.Event.commune,
        models.Event.postal_code,
        models.Event.date_begin,
        models.Event.date_end,
        models.Event.category_id,
        models.Event.status,
        models.Event.cost,
        models.Event.remaining_spots,
        models.Event.registration_required,
        models.Event.is_volunteering,
    )
    query = query.filter(models.Event.is_active.is_(True))
    if wilaya is not None:
        query = query.filter(models.Event.wilaya == wilaya)
    if commune is not None:
        query = query.filter(models.Event.commune == commune)
    if category_ids:
        query = query.filter(models.Event.category_id.in_(category_ids))
    if status is not None:
        query = query.filter(models.Event.status == status)
    return query.offset(skip).limit(limit).all()


def create_event(db: Session, data: EventCreate) -> models.Event:
    event_data = data.dict()
    input_language = event_data.pop("input_language", "fr")
    if event_data.get("capacity") is not None:
        event_data["remaining_spots"] = event_data["capacity"]

    if input_language == "fr":
        if event_data.get("title_fr") is None:
            event_data["title_fr"] = event_data["title"]
        if event_data.get("description_fr") is None and event_data.get("description") is not None:
            event_data["description_fr"] = event_data["description"]
    elif input_language == "ar":
        if event_data.get("title_ar") is None:
            event_data["title_ar"] = event_data["title"]
        if event_data.get("description_ar") is None and event_data.get("description") is not None:
            event_data["description_ar"] = event_data["description"]
    elif input_language == "tzm":
        if event_data.get("title_tam") is None:
            event_data["title_tam"] = event_data["title"]
        if event_data.get("description_tam") is None and event_data.get("description") is not None:
            event_data["description_tam"] = event_data["description"]

    event = models.Event(**event_data)
    translations = translate_event_fields(
        title=data.title,
        description=data.description,
        from_lang=data.input_language,
    )

    if "title_ar" in translations and not event.title_ar:
        event.title_ar = translations["title_ar"]
    if "title_fr" in translations and not event.title_fr:
        event.title_fr = translations["title_fr"]
    if "description_ar" in translations and not event.description_ar:
        event.description_ar = translations["description_ar"]
    if "description_fr" in translations and not event.description_fr:
        event.description_fr = translations["description_fr"]

    db.add(event)
    db.commit()
    db.refresh(event)

    # Generate and store embedding (non-blocking)
    try:
        event_text = build_event_text(event)
        embedding = embed_text(event_text)
        upsert_event_embedding(event.id, embedding)
    except Exception as e:
        print(f"⚠️ Embedding failed for event {event.id}: {e}")

    return event


def update_event(db: Session, event_id: int, data: EventUpdate) -> Optional[models.Event]:
    event = get_event(db, event_id)
    if event is None:
        return None

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    db.add(event)
    db.commit()
    db.refresh(event)

    # Regenerate and update embedding (non-blocking)
    try:
        event_text = build_event_text(event)
        embedding = embed_text(event_text)
        upsert_event_embedding(event.id, embedding)
    except Exception as e:
        print(f"⚠️ Embedding failed for event {event.id}: {e}")

    return event


def deactivate_event(db: Session, event_id: int) -> Optional[models.Event]:
    event = get_event(db, event_id)
    if event is None:
        return None

    event.is_active = False
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_events_by_category(db: Session, category_id: int) -> List[models.Event]:
    return (
        db.query(models.Event)
        .filter(models.Event.category_id == category_id)
        .filter(models.Event.is_active.is_(True))
        .all()
    )
