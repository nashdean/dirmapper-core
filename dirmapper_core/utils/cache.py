import hashlib
import functools
import json
import re
from typing import Optional, Dict, Any, Union, List
from dirmapper_core.models.directory_structure import DirectoryStructure
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
    
    def clear(self):
        """Clear all cache entries."""
        try:
            self.cache.clear()
            logger.info("Cache cleared successfully.")
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")

    def get_directory_key(self, directory_path: str, items_hash: str, level: Optional[int] = None) -> str:
        """
        Generate a cache key for directory summaries.
        
        Args:
            directory_path (str): Path to the directory
            items_hash (str): Hash of the directory's contents
            level (Optional[int]): Directory level for level-based caching
            
        Returns:
            str: Cache key for the directory
        """
        normalized_path = self._normalize_context(directory_path)
        context = f"{normalized_path}_{items_hash}"
        if level is not None:
            context += f"_level_{level}"
        return f"dir_{hashlib.sha256(context.encode()).hexdigest()[:32]}"

    def get_parent_context_key(self, directory_path: str, parent_level: int) -> str:
        """Generate a cache key for parent directory context."""
        normalized_path = self._normalize_context(directory_path)
        return f"parent_{hashlib.sha256(f'{normalized_path}_{parent_level}'.encode()).hexdigest()[:32]}"

    def _get_contents_hash(self, items: List[Dict[str, Any]]) -> str:
        """Generate a hash of directory contents for cache invalidation."""
        # Sort items by path for consistent hashing
        sorted_items = sorted(items, key=lambda x: x.get('path', ''))
        content = json.dumps(sorted_items, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

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

    def get_project_summary_key(self, directory_structure: 'DirectoryStructure') -> str:
        """
        Generate a cache key for project-level summaries.
        
        Args:
            directory_structure (DirectoryStructure): The directory structure being summarized
            
        Returns:
            str: Cache key for the project summary
        """
        # Include summaries in the hash to ensure cache invalidation when any summary changes
        summaries = "_".join(
            f"{item.path}:{item.short_summary}" 
            for item in directory_structure.items 
            if item.short_summary
        )
        summary_hash = hashlib.sha256(summaries.encode()).hexdigest()[:16]
        return f"project_{directory_structure.content_hash}_{summary_hash}"

    def get_cache_name(self, obj: Any, func_name: str = "") -> tuple[str, str]:
        """
        Get a human-readable cache name and type for any supported object.
        
        Args:
            obj: The object to generate a cache name for
            func_name: The name of the function being cached
            
        Returns:
            tuple[str, str]: (cache_name, cache_type)
        """
        from dirmapper_core.models.directory_structure import DirectoryStructure
        from dirmapper_core.models.directory_item import DirectoryItem

        # Check function name first for special cases
        if "_generate_project_summary" in func_name:
            return "", "project summary"
            
        if isinstance(obj, DirectoryStructure):
            if obj.items:
                root_dir = obj.items[0].path.split('/')[-1]
                return f"{root_dir}", "directory structure"
            return "Empty directory structure", "directory structure"
            
        elif isinstance(obj, DirectoryItem):
            return obj.name, "file"
            
        elif isinstance(obj, str):
            # For strings (like raw content or file paths)
            if '/' in obj:  # If it's a path, just show the filename
                return obj.split('/')[-1], "file"
            if len(obj) > 30:  # If it's content, show truncated version
                return f"{obj[:30]}...", "content"
            return obj, "content"
            
        return "unknown", "unknown"

    def get_cache_key_with_type(self, content: Union[str, Dict], context: str = "", cache_type: str = "") -> str:
        """
        Generate a consistent cache key that includes the type of content being cached.
        
        Args:
            content: The content to hash
            context: Additional context for the key
            cache_type: Type of content being cached (e.g., "file", "directory", "project")
            
        Returns:
            str: Cache key including type information
        """
        basic_key = self.get_cache_key(content, context)
        return f"{cache_type}_{basic_key}" if cache_type else basic_key

    def get_paginated_structure_key(self, directory_structure: 'DirectoryStructure', page_index: int, total_pages: int) -> str:
        """
        Generate a cache key for paginated directory structures.
        
        Args:
            directory_structure (DirectoryStructure): The directory structure
            page_index (int): Current page index
            total_pages (int): Total number of pages
            
        Returns:
            str: Cache key for the paginated structure
        """
        return f"page_{page_index}_of_{total_pages}_{directory_structure.content_hash}"

def cached_api_call(func):
    """Decorator to cache API calls with improved logging."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'cache'):
            return func(self, *args, **kwargs)

        try:
            # Get the first argument as our main object
            obj = args[0] if args else None
            
            # Get cache name and type using the cache manager, passing function name
            cache_name, cache_type = self.cache.get_cache_name(obj, func.__name__)
            
            # Generate cache key components
            components = [
                func.__name__,
                obj.content_hash if hasattr(obj, 'content_hash') else '',
                str(kwargs)
            ]
            
            # Generate cache key with type information
            cache_key = self.cache.get_cache_key_with_type(
                '_'.join(components),
                getattr(self, 'cache_context', ''),
                cache_type
            )
            
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"🔵 Using cached {cache_type} for {cache_name}")
                return cached_result
            
            logger.info(f"🔴 Cache miss - sending API request for {cache_type} {cache_name}")
            result = func(self, *args, **kwargs)
            
            # Store in cache if result is valid
            if result and (isinstance(result, (dict, str)) and (isinstance(result, str) or any(result.values()))):
                self.cache.set(cache_key, result)
            
            stats = self.cache.get_stats()
            logger.debug(f"Cache stats: {stats['hits']} hits, {stats['misses']} misses "
                      f"({stats['hit_rate']:.1f}% hit rate)")
            
            return result
            
        except Exception as e:
            logger.error(f"Cache operation failed for {cache_name}: {str(e)}")
            return func(self, *args, **kwargs)
            
    return wrapper
