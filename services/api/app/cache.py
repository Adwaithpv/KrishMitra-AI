"""
Redis caching service for improved performance
"""

import json
import hashlib
import os
from typing import Optional, Any, Dict
import logging

try:
    import redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service"""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = False
        self._setup_redis()
    
    def _setup_redis(self):
        """Setup Redis connection"""
        if not redis:
            logger.warning("Redis not available, caching disabled")
            return
        
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
            self.redis_client = None
            self.enabled = False
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a consistent cache key from parameters"""
        # Sort kwargs for consistent hashing
        sorted_params = sorted(kwargs.items())
        param_str = json.dumps(sorted_params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"{prefix}:{param_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (seconds)"""
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            logger.error(f"Cache info error: {e}")
            return {"enabled": True, "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

# Caching decorators
def cache_query_result(ttl: int = 1800):  # 30 minutes default
    """Decorator to cache query results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_service = get_cache_service()
            
            # Generate cache key from function name and arguments
            cache_key = cache_service._generate_cache_key(
                f"query:{func.__name__}",
                args=str(args),
                **kwargs
            )
            
            # Try to get from cache first
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            logger.info(f"Cache miss for {cache_key}, result cached")
            
            return result
        return wrapper
    return decorator

def cache_embeddings(ttl: int = 86400):  # 24 hours default
    """Decorator to cache embedding computations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_service = get_cache_service()
            
            # Generate cache key from text content
            cache_key = cache_service._generate_cache_key(
                "embeddings",
                **kwargs
            )
            
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Global cache service instance
_cache_service = None

def get_cache_service() -> CacheService:
    """Get or create cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
