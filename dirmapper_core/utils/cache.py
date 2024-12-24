import hashlib
import functools
from typing import Optional, Dict, Any
import diskcache
from dirmapper_core.utils.logger import logger

class SummaryCache:
    """Cache for API responses to avoid redundant calls."""
    
    def __init__(self, cache_dir: str = ".summary_cache", ttl_days: int = 7):
        """
        Initialize the cache with a directory and TTL.

        Args:
            cache_dir (str): Directory to store cache files
            ttl_days (int): Number of days before cache entries expire
        """
        self.cache = diskcache.Cache(cache_dir)
        self.ttl = ttl_days * 24 * 60 * 60  # Convert days to seconds
        self.hits = 0
        self.misses = 0

    def get_cache_key(self, content: str, context: str = "") -> str:
        """Generate a cache key from content and context."""
        return hashlib.sha256(f"{content}{context}".encode()).hexdigest()

    def get(self, key: str) -> Optional[Dict]:
        """Get cached summary if it exists and is not expired."""
        try:
            result = self.cache.get(key)
            if result is not None:
                self.hits += 1
                logger.debug(f"Cache hit [{self.hits} hits, {self.misses} misses]")
            else:
                self.misses += 1
                logger.debug(f"Cache miss [{self.hits} hits, {self.misses} misses]")
            return result
        except Exception as e:
            logger.error(f"Cache retrieval error: {str(e)}")
            return None

    def set(self, key: str, value: Dict):
        """Cache a summary with TTL."""
        try:
            self.cache.set(key, value, expire=self.ttl)
        except Exception as e:
            logger.error(f"Cache storage error: {str(e)}")

    def get_stats(self) -> Dict[str, int]:
        """Get cache performance statistics."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": (self.hits / (self.hits + self.misses)) * 100 if (self.hits + self.misses) > 0 else 0
        }

def cached_api_call(func):
    """
    Decorator to cache API calls with improved logging.
    
    Usage:
        @cached_api_call
        def my_api_method(self, *args, **kwargs):
            # Method implementation
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, 'cache'):
            try:
                # Generate a readable cache key description
                desc = f"{func.__name__}({args[0] if args else ''})"  # Usually the first arg is file_name
                cache_key = self.cache.get_cache_key(str(args) + str(kwargs))
                
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    logger.info(f"🔵 Using cached summary for {desc}")
                    return cached_result
                
                logger.info(f"🔴 Cache miss - sending API request for {desc}")
                result = func(self, *args, **kwargs)
                self.cache.set(cache_key, result)
                
                # Log cache statistics periodically
                stats = self.cache.get_stats()
                logger.info(f"Cache stats: {stats['hits']} hits, {stats['misses']} misses "
                          f"({stats['hit_rate']:.1f}% hit rate)")
                
                return result
            except Exception as e:
                logger.error(f"Cache operation failed for {desc}: {str(e)}")
                return func(self, *args, **kwargs)
        return func(self, *args, **kwargs)
    return wrapper
