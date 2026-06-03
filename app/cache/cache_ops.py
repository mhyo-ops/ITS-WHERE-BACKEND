from __future__ import annotations
import hashlib
from typing import Optional

import redis.asyncio as redis


def make_cache_key(
    query: str,
    wilaya: str | None,
    category: str | None,
    language: str | None,
) -> str:
    normalized_query = query.strip().lower()
    concatenated = f"{normalized_query}|{wilaya or ''}|{category or ''}|{language or ''}"
    fingerprint = hashlib.sha256(concatenated.encode()).hexdigest()
    return f"query:{fingerprint}"


async def get_cached(redis_client: redis.Redis, key: str) -> Optional[str]:
    return await redis_client.get(key)


async def set_cached(redis_client: redis.Redis, key: str, value: str, ttl_seconds: int = 3600) -> None:
    await redis_client.set(key, value, ex=ttl_seconds)


async def invalidate_all(redis_client: redis.Redis) -> None:
    keys = await redis_client.keys("query:*")
    if not keys:
        return
    await redis_client.delete(*keys)


def make_event_list_key(
    wilaya: str | None,
    postal_code: str | None,
    category_id: int | None,
    status: str | None,
    skip: int,
    limit: int,
    lang: str,
) -> str:
    parts = [
        f"w:{wilaya or ''}",
        f"p:{postal_code or ''}",
        f"c:{category_id or ''}",
        f"s:{status or ''}",
        f"sk:{skip}",
        f"l:{limit}",
        f"lang:{lang}",
    ]
    raw = "|".join(parts)
    return "events:" + hashlib.md5(raw.encode()).hexdigest()


def make_event_detail_key(event_id: int, lang: str) -> str:
    return f"event_detail:{event_id}:{lang}"


async def invalidate_event_list_cache(redis_client: redis.Redis) -> int:
    keys = await redis_client.keys("events:*")
    if not keys:
        return 0
    deleted = await redis_client.delete(*keys)
    return deleted


def make_discover_key(
    scope: str,
    value: str,
    fav_ids: list[int],
    status: str | None,
    skip: int,
    limit: int,
    lang: str,
) -> str:
    fav_str = ",".join(str(i) for i in sorted(fav_ids))
    raw = f"{scope}:{value}|favs:{fav_str}|lang:{lang}|s:{status or ''}|sk:{skip}|l:{limit}"
    return "discover:" + hashlib.md5(raw.encode()).hexdigest()


async def invalidate_discover_cache(redis_client: redis.Redis) -> int:
    keys = await redis_client.keys("discover:*")
    if not keys:
        return 0
    deleted = await redis_client.delete(*keys)
    return deleted
