from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class EventBase(BaseModel):
    category_id: int
    title: str
    title_ar: str | None = None
    title_fr: str | None = None
    title_tam: str | None = None
    description: str | None = None
    description_ar: str | None = None
    description_fr: str | None = None
    description_tam: str | None = None
    address: str
    postal_code: str
    commune: str
    wilaya: str
    date_begin: datetime
    date_end: datetime | None = None
    capacity: int | None = None
    remaining_spots: int | None = None
    registration_link: str | None = None
    registration_contact: str | None = None
    registration_required: bool = False
    is_volunteering: bool = False
    volunteer_skills: str | None = None
    cost: str = "Free"
    status: str = "upcoming"


class EventCreate(EventBase):
    input_language: str = "fr"

    @field_validator("input_language")
    @classmethod
    def validate_input_language(cls, value: str) -> str:
        if value not in ["fr", "ar", "tzm"]:
            raise ValueError("Language must be fr, ar, or tzm")
        return value


class EventUpdate(BaseModel):
    category_id: int | None = None
    title: str | None = None
    title_ar: str | None = None
    title_fr: str | None = None
    title_tam: str | None = None
    description: str | None = None
    description_ar: str | None = None
    description_fr: str | None = None
    description_tam: str | None = None
    address: str | None = None
    postal_code: str | None = None
    commune: str | None = None
    wilaya: str | None = None
    date_begin: datetime | None = None
    date_end: datetime | None = None
    capacity: int | None = None
    remaining_spots: int | None = None
    registration_link: str | None = None
    registration_contact: str | None = None
    registration_required: bool | None = None
    is_volunteering: bool | None = None
    volunteer_skills: str | None = None
    cost: str | None = None
    status: str | None = None
    is_active: bool | None = None


class EventRead(EventBase):
    id: int
    is_active: bool
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
