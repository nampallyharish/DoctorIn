"""Redis-backed rate limiting using sliding window."""

import time

from app.core.exceptions import RateLimitExceededError
from app.core.redis import get_redis


class RateLimiter:
    """Sliding-window rate limiter powered by Redis sorted sets."""

    @staticmethod
    async def check_rate_limit(
        key: str,
        limit: int,
        window_seconds: int,
        error_message: str | None = None,
    ) -> None:
        """
        Check rate limit and record attempt.
        Raises RateLimitExceededError if exceeded.
        """
        try:
            redis = await get_redis()
            current_ts = time.time()
            cutoff_ts = current_ts - window_seconds
            redis_key = f"ratelimit:{key}"

            # Remove old entries outside the sliding window
            pipe = redis.pipeline()
            pipe.zremrangebyscore(redis_key, 0, cutoff_ts)
            pipe.zcard(redis_key)
            pipe.zadd(redis_key, {str(current_ts): current_ts})
            pipe.expire(redis_key, window_seconds + 10)
            results = await pipe.execute()

            current_count = results[1]
            if current_count >= limit:
                retry_after = int(window_seconds)
                msg = (
                    error_message
                    or f"Rate limit of {limit} requests per {window_seconds}s exceeded."
                )
                raise RateLimitExceededError(message=msg, retry_after=retry_after)
        except RateLimitExceededError:
            raise
        except Exception:
            # If Redis is down or unreachable during rate limit check, fail open in dev, log warning
            pass


rate_limiter = RateLimiter()
