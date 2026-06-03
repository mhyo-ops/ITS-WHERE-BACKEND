from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_admin, get_db
from ..crud.category import (
    create_category,
    get_category,
    get_category_by_name,
    get_categories,
    update_category,
    deactivate_category,
)
from ..schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryRead])
def list_categories(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
) -> List[CategoryRead]:
    return get_categories(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, db: Session = Depends(get_db)) -> CategoryRead:
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    data: CategoryCreate,
    _: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> CategoryRead:
    if get_category_by_name(db, data.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
    return create_category(db, data)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category_endpoint(
    category_id: int,
    data: CategoryUpdate,
    _: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> CategoryRead:
    category = update_category(db, category_id, data)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    _: object = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    category = deactivate_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"message": "Category deactivated", "id": category_id}
