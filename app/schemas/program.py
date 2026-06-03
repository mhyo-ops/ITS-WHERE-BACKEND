from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProgramBase(BaseModel):
    title: str
    description: str
    category: str
    language: str
    capacity: Optional[int] = None
    is_active: bool = True


class ProgramCreate(ProgramBase):
    center_id: int


class ProgramUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class ProgramRead(ProgramBase):
    id: int
    center_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
