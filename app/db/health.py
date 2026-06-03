from __future__ import annotations
import asyncio

from fastapi import Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from .base import get_db


async def db_health_check(db: Session = Depends(get_db)) -> dict:
    try:
        await asyncio.to_thread(db.execute, text("SELECT 1"))
        return {"database": "healthy", "type": "postgresql"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {e}") from e
