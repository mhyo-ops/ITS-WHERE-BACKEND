from __future__ import annotations
from typing import Dict

from qdrant_client.models import PointStruct
from sqlalchemy.orm import Session

from .embeddings import embed
from .qdrant_client import get_client
from ..core.config import settings
from ..db import models


def ingest_center(center: models.YouthCenter) -> None:
    text = f"{center.name}. {center.description}. Wilaya: {center.wilaya}."
    vector = embed(text)
    payload = {
        "type": "center",
        "center_id": center.id,
        "name": center.name,
        "wilaya": center.wilaya,
        "languages": center.languages,
        "is_active": center.is_active,
    }
    # Use integer point IDs to avoid collisions: centers are multiples of 10.
    point_id = center.id * 10
    get_client().upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=[PointStruct(id=point_id, vector=vector, payload=payload)],
    )


def ingest_program(program: models.Program, center: models.YouthCenter) -> None:
    text = (
        f"{program.title}. {program.description}. "
        f"Category: {program.category}. "
        f"Center: {center.name}. Wilaya: {center.wilaya}."
    )
    vector = embed(text)
    payload = {
        "type": "program",
        "program_id": program.id,
        "center_id": program.center_id,
        "title": program.title,
        "wilaya": center.wilaya,
        "category": program.category,
        "language": program.language,
        "is_active": program.is_active,
    }
    # Program IDs are point_id = program.id * 10 + 1 to prevent center collisions.
    point_id = program.id * 10 + 1
    get_client().upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=[PointStruct(id=point_id, vector=vector, payload=payload)],
    )


def ingest_all(db: Session) -> Dict[str, int]:
    centers = db.query(models.YouthCenter).filter(models.YouthCenter.is_active == True).all()
    programs = db.query(models.Program).filter(models.Program.is_active == True).all()
    center_map = {center.id: center for center in centers}

    for center in centers:
        ingest_center(center)

    for program in programs:
        center = center_map.get(program.center_id)
        if center is None:
            continue
        ingest_program(program, center)

    total = len(centers) + len(programs)
    return {
        "centers_ingested": len(centers),
        "programs_ingested": len(programs),
        "total_vectors": total,
    }


def delete_document(point_id: int) -> None:
    get_client().delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=[point_id],
    )
