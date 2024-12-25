import hashlib
import functools
import re
from typing import Optional, Dict, Any, Union
import diskcache
from dirmapper_core.utils.logger import logger

class SummaryCache:
    """Cache for API responses to avoid redundant calls."""
    
    def __init__(self, cache_dir: str = ".summary_cache", ttl_days: int = 30):  # Increased TTL to 30 days
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

    def _normalize_content(self, content: str) -> str:
        """Normalize content to increase cache hits."""
        # Remove whitespace variations
        content = re.sub(r'\s+', ' ', content.strip())
        # Remove common variable content like timestamps
        content = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'TIMESTAMP', content)
        return content

    def _normalize_context(self, context: str) -> str:
        """Normalize context information."""
        # Remove path variations
        context = re.sub(r'[\/\\]+', '/', context)
        # Remove user-specific paths
        context = re.sub(r'/Users/[^/]+/', '/USER/', context)
        return context

    def get_cache_key(self, content: Union[str, Dict], context: str = "") -> str:
        """Generate a consistent cache key from normalized content and context."""
        if isinstance(content, dict):
            # Sort dictionary keys for consistent hashing
            content = json.dumps(content, sort_keys=True)
        
        normalized_content = self._normalize_content(str(content))
        normalized_context = self._normalize_context(context)
        
        # Include only relevant parts of the content for hashing
        content_hash = hashlib.sha256(normalized_content.encode()).hexdigest()
        context_hash = hashlib.sha256(normalized_context.encode()).hexdigest()
        
        return f"{context_hash[:8]}_{content_hash[:24]}"

    def get_chunk_key(self, file_name: str, chunk_index: int, total_chunks: int) -> str:
        """
        Generate a consistent key for file chunks.
        
        Args:
            file_name (str): Name of the file being chunked
            chunk_index (int): Index of current chunk
            total_chunks (int): Total number of chunks
            
        Returns:
            str: A consistent cache key for the chunk
        """
        normalized_name = self._normalize_context(file_name)
        chunk_context = f"{normalized_name}_chunk_{chunk_index}_of_{total_chunks}"
        return hashlib.sha256(chunk_context.encode()).hexdigest()[:32]

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
        if not hasattr(self, 'cache'):
            return func(self, *args, **kwargs)

        try:
            # Generate consistent cache key
            file_name = args[0] if args else ""
            content = args[1] if len(args) > 1 else ""
            
            # Include relevant parameters in cache key
            params = {
                'max_length': kwargs.get('max_length', 0),
                'is_short': kwargs.get('is_short', False)
            }
            
            cache_key = self.cache.get_cache_key(
                content,
                f"{func.__name__}_{file_name}_{params}"
            )
            
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"🔵 Using cached summary for {file_name}")
                return cached_result
            
            logger.info(f"🔴 Cache miss - sending API request for {file_name}")
            result = func(self, *args, **kwargs)
            
            # Store in cache if result is valid
            if result and (isinstance(result, dict) and any(result.values())):
                self.cache.set(cache_key, result)
            
            stats = self.cache.get_stats()
            logger.info(f"Cache stats: {stats['hits']} hits, {stats['misses']} misses "
                       f"({stats['hit_rate']:.1f}% hit rate)")
            
            return result
            
        except Exception as e:
            logger.error(f"Cache operation failed for {file_name}: {str(e)}")
            return func(self, *args, **kwargs)
            
    return wrapper
