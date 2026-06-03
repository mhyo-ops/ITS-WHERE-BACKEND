from __future__ import annotations
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminLogin(BaseModel):
    admin_slug: str
    password: str


class AdminRead(BaseModel):
    id: int
    admin_slug: str
    created_at: datetime
    last_login: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
