from __future__ import annotations
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..db import models
from ..schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.name == name).first()


def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[models.Category]:
    query = db.query(models.Category)
    if active_only:
        query = query.filter(models.Category.is_active.is_(True))
    return query.offset(skip).limit(limit).all()


def create_category(db: Session, data: CategoryCreate) -> models.Category:
    if get_category_by_name(db, data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists",
        )

    category = models.Category(**data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Optional[models.Category]:
    category = get_category(db, category_id)
    if category is None:
        return None

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def deactivate_category(db: Session, category_id: int) -> Optional[models.Category]:
    category = get_category(db, category_id)
    if category is None:
        return None

    category.is_active = False
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
