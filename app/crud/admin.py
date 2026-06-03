from __future__ import annotations
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import hash_password
from ..db import models


def get_admin_by_slug(db: Session, slug: str) -> models.AdminUser | None:
    return db.query(models.AdminUser).filter(models.AdminUser.admin_slug == slug).first()


def create_admin(db: Session, slug: str, password: str) -> models.AdminUser:
    if get_admin_by_slug(db, slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin slug already exists",
        )

    admin = models.AdminUser(
        admin_slug=slug,
        hashed_password=hash_password(password),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def update_last_login(db: Session, admin_id: int) -> None:
    admin = db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    admin.last_login = datetime.utcnow()
    db.add(admin)
    db.commit()
