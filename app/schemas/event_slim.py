from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventSlim(BaseModel):
    id: int
    title: str
    title_ar: str | None = None
    title_fr: str | None = None
    title_tam: str | None = None
    wilaya: str
    commune: str
    postal_code: str
    date_begin: datetime
    date_end: datetime | None = None
    category_id: int
    status: str
    cost: str
    remaining_spots: int | None = None
    registration_required: bool
    is_volunteering: bool

    model_config = ConfigDict(from_attributes=True)
