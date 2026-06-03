from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.base import get_db
from app.db.models import AdminUser, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/user/login")


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    token_data = decode_token(token)
    if token_data.role != "user":
        raise _credentials_exception()

    user = db.query(User).filter(User.email == token_data.subject).first()
    if user is None or not user.is_active:
        raise _credentials_exception()
    return user


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    token_data = decode_token(token)
    if token_data.role != "admin":
        raise _credentials_exception()

    admin = db.query(AdminUser).filter(AdminUser.admin_slug == token_data.subject).first()
    if admin is None:
        raise _credentials_exception()
    return admin
