import os
from typing import Optional

_cached_client = None

def get_redis():
    global _cached_client
    if _cached_client is not None:
        return _cached_client
    try:
        import redis  # type: ignore
        url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _cached_client = redis.Redis.from_url(url, decode_responses=True)
        # Ping to verify connectivity
        _cached_client.ping()
        return _cached_client
    except Exception:
        return None


