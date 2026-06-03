from __future__ import annotations

import redis.asyncio as redis
from fastapi import Depends

from ..core.config import settings


_redis_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def get_redis() -> redis.Redis:
    return _get_client()


async def get_redis_dependency(redis_client: redis.Redis = Depends(get_redis)) -> redis.Redis:
    return redis_client
