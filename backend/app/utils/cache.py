"""Caching utilities for performance optimization.

Provides in-memory caching with TTL (Time To Live) for frequently accessed data.
"""

import time
import threading
from typing import Any, Optional, Dict
from functools import wraps


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if it exists and hasn't expired."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() < entry['expires_at']:
                    return entry['value']
                else:
                    # Entry has expired, remove it
                    del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL (time to live in seconds)."""
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries and return count of removed entries."""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time >= entry['expires_at']
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)


# Global cache instance
cache = SimpleCache()


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        key_prefix: Prefix for cache key (default: function name)
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call the function and cache the result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        # Return the appropriate wrapper based on whether the function is async
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x0080:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def invalidate_cache(key_pattern: str = ""):
    """Invalidate cache entries matching a pattern."""
    with cache._lock:
        if not key_pattern:
            cache.clear()
        else:
            keys_to_delete = [key for key in cache._cache.keys() if key.startswith(key_pattern)]
            for key in keys_to_delete:
                del cache._cache[key]


# Periodic cleanup thread
def _cleanup_worker():
    """Background worker to periodically clean up expired cache entries."""
    while True:
        try:
            time.sleep(60)  # Run cleanup every minute
            removed_count = cache.cleanup_expired()
            if removed_count > 0:
                from app.utils.logger import setup_logging
                logger = setup_logging(__name__)
                logger.info(f"Cleaned up {removed_count} expired cache entries")
        except Exception as e:
            from app.utils.logger import setup_logging
            logger = setup_logging(__name__)
            logger.error(f"Error in cache cleanup worker: {e}")


# Start cleanup worker in background thread
cleanup_thread = threading.Thread(target=_cleanup_worker, daemon=True)
cleanup_thread.start()