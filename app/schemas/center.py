from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class YouthCenterBase(BaseModel):
    name: str
    wilaya: str
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    languages: str = "fr"
    is_active: bool = True


class YouthCenterCreate(YouthCenterBase):
    pass


class YouthCenterUpdate(BaseModel):
    name: Optional[str] = None
    wilaya: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    languages: Optional[str] = None
    is_active: Optional[bool] = None


class YouthCenterRead(YouthCenterBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
