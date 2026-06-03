from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    preferred_language: str = "fr"
    postal_code: str | None = None

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        if value not in ["fr", "ar", "tzm"]:
            raise ValueError("Language must be fr, ar, or tzm")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class MessageResponse(BaseModel):
    message: str


class UserRead(BaseModel):
    id: int
    email: str
    username: str
    preferred_language: str
    postal_code: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    preferred_language: str | None = None
    postal_code: str | None = None

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in ["fr", "ar", "tzm"]:
            raise ValueError("Language must be fr, ar, or tzm")
        return value
