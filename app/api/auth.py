from __future__ import annotations
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import redis.asyncio as redis

from ..cache.redis_client import get_redis
from ..core.dependencies import get_db
from ..core.email import generate_code, send_verification_email, send_reset_email
from ..core.security import create_access_token, verify_password
from ..crud import user as crud_user
from ..crud import admin as crud_admin
from ..schemas.admin import AdminLogin
from ..schemas.token import Token
from ..schemas.user import (
    UserLogin,
    UserRead,
    UserRegister,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/user/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    data: UserRegister,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> UserRead:
    user = crud_user.create_user(db, data)

    # Generate verification code
    code = generate_code()

    # Store in Redis with TTL 600s
    await redis_client.setex(f"verify:{data.email}", 600, code)

    # Send verification email (non-blocking, never block registration)
    try:
        await send_verification_email(data.email, code)
    except Exception as e:
        print(f"⚠️ Email send failed: {e}")

    return user


@router.post("/user/verify-email", response_model=MessageResponse)
async def verify_email(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> MessageResponse:
    # Fetch code from Redis
    stored_code = await redis_client.get(f"verify:{data.email}")

    if stored_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code expired or not found",
        )

    if stored_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code",
        )

    # Update user is_verified
    user = crud_user.get_user_by_email(db, data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    crud_user.verify_user_email(db, user.id)

    # Delete Redis key
    await redis_client.delete(f"verify:{data.email}")

    return MessageResponse(message="Email verified successfully")


@router.post("/user/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> MessageResponse:
    # Look up user by email — if not found, return 200 anyway (no enumeration)
    user = crud_user.get_user_by_email(db, data.email)

    if user is not None:
        # Generate code
        code = generate_code()

        # Store in Redis: await redis.setex(f"reset:{email}", 600, code)
        await redis_client.setex(f"reset:{data.email}", 600, code)

        # Send reset email (non-blocking try/except)
        try:
            await send_reset_email(data.email, code)
        except Exception as e:
            print(f"⚠️ Email send failed: {e}")

    return MessageResponse(message="If this email exists, a reset code was sent")


@router.post("/user/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> MessageResponse:
    # Fetch from Redis
    stored_code = await redis_client.get(f"reset:{data.email}")

    if stored_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code expired or not found",
        )

    if stored_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code",
        )

    # Get user and update password
    user = crud_user.get_user_by_email(db, data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    crud_user.update_user_password(db, user.id, data.new_password)

    # Delete Redis key
    await redis_client.delete(f"reset:{data.email}")

    return MessageResponse(message="Password reset successfully")


@router.post("/user/login", response_model=Token)
def login_user(data: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = crud_user.get_user_by_email(db, data.email)
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=user.email, role="user")
    return Token(access_token=access_token)


@router.post("/admin/login", response_model=Token)
def login_admin(data: AdminLogin, db: Session = Depends(get_db)) -> Token:
    admin = crud_admin.get_admin_by_slug(db, data.admin_slug)
    if admin is None or not verify_password(data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    crud_admin.update_last_login(db, admin.id)
    access_token = create_access_token(subject=admin.admin_slug, role="admin")
    return Token(access_token=access_token)
