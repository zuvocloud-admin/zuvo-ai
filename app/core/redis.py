import time
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger


class IdempotencyCache:
    """
    Manages deduplication of incoming WhatsApp messages via 'wamid'.
    Supports Async Redis with an automatic In-Memory fallback for local development.
    """

    def __init__(self):
        self._redis_client: Optional[aioredis.Redis] = None
        self._in_memory_cache: dict[str, float] = {}
        self._is_redis_available = False

    async def connect(self):
        try:
            self._redis_client = aioredis.from_url(
                settings.redis.url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0
            )
            await self._redis_client.ping()
            self._is_redis_available = True
            logger.info("Connected to Redis successfully for message deduplication.")
        except Exception as e:
            self._is_redis_available = False
            logger.warning(f"Redis unavailable ({e}). Falling back to internal in-memory idempotency cache.")

    async def disconnect(self):
        if self._redis_client:
            await self._redis_client.close()
            logger.info("Redis connection closed.")

    async def is_duplicate(self, wamid: str) -> bool:
        """
        Returns True if the wamid has already been received within the TTL window.
        Otherwise records the wamid and returns False.
        """
        if not wamid:
            return False

        key = f"zuvo:wamid:{wamid}"
        ttl = settings.redis.idempotency_ttl_seconds

        if self._is_redis_available and self._redis_client:
            try:
                # SETNX key 1 EX ttl
                is_new = await self._redis_client.set(key, "1", ex=ttl, nx=True)
                return not is_new
            except Exception as e:
                logger.error(f"Redis idempotency check failed: {e}. Falling back to memory.")

        # In-memory fallback
        now = time.time()
        # Clean expired keys occasionally
        if len(self._in_memory_cache) > 10000:
            self._in_memory_cache = {k: exp for k, exp in self._in_memory_cache.items() if exp > now}

        if key in self._in_memory_cache and self._in_memory_cache[key] > now:
            return True

        self._in_memory_cache[key] = now + ttl
        return False


# Global singleton instance
idempotency_cache = IdempotencyCache()
