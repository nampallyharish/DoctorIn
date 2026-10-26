"""Redis connection management."""


import redis.asyncio as aioredis

from app.config import get_settings
from app.core.logging import logger

settings = get_settings()

redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get active Redis client instance."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
        )
    return redis_client


async def close_redis() -> None:
    """Close Redis connection pool on app shutdown."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None


async def check_redis_health() -> bool:
    """Verify Redis connection health."""
    try:
        client = await get_redis()
        return bool(await client.ping())
    except Exception as exc:
        logger.error(f"Redis health check failed: {exc}")
        return False
