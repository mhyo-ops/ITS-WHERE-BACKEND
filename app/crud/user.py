from __future__ import annotations

from typing import Optional
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import hash_password
from ..db import models
from ..schemas.user import UserRegister, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, data: UserRegister) -> models.User:
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    if get_user_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user_data = data.dict(exclude={"password"})
    user = models.User(
        **user_data,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[models.User]:
    user = get_user(db, user_id)
    if user is None:
        return None

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: int) -> Optional[models.User]:
    user = get_user(db, user_id)
    if user is None:
        return None

    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_user_email(db: Session, user_id: int) -> Optional[models.User]:
    user = get_user(db, user_id)
    if user is None:
        return None

    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user_id: int, new_password: str) -> Optional[models.User]:
    user = get_user(db, user_id)
    if user is None:
        return None

    user.hashed_password = hash_password(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_favourite_category(db: Session, user_id: int, category_id: int) -> models.User:
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if category in user.favourite_categories:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already in favourites")

    user.favourite_categories.append(category)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def remove_favourite_category(db: Session, user_id: int, category_id: int) -> models.User:
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None or category not in user.favourite_categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found in favourites")

    user.favourite_categories.remove(category)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def register_event(db: Session, user_id: int, event_id: int) -> models.User:
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None or not event.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found or inactive")

    if event in user.registered_events:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered for event")

    if event.remaining_spots == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No remaining spots available")

    user.registered_events.append(event)
    if event.remaining_spots is not None:
        event.remaining_spots -= 1

    db.add(user)
    db.add(event)
    db.commit()
    db.refresh(user)
    return user


def unregister_event(db: Session, user_id: int, event_id: int) -> models.User:
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None or event not in user.registered_events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not registered for this event")

    user.registered_events.remove(event)
    if event.remaining_spots is not None:
        event.remaining_spots += 1

    db.add(user)
    db.add(event)
    db.commit()
    db.refresh(user)
    return user
