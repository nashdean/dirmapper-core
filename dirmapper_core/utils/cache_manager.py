import os
from pathlib import Path
from typing import Any, Dict, Optional, List
import diskcache
from dirmapper_core.utils.logger import logger

# TODO: Does not work with nested cache entries; need to fix this in future to remove individual entries
# class CacheManager:
#     def __init__(self, cache_dir: str = ".summary_cache"):
#         self.cache_dir = Path(cache_dir)
#         self.cache = diskcache.Cache(str(self.cache_dir))
    
#     def list_entries(self) -> List[str]:
#         """List all cache keys."""
#         return list(self.cache.iterkeys())
    
#     def remove_entry(self, key: str) -> bool:
#         """Remove specific cache entry."""
#         try:
#             del self.cache[key]
#             return True
#         except KeyError:
#             return False
    
#     def get_value(self, key: str) -> Dict[str, Any]:
#         """Get the full value for a cache entry."""
#         try:
#             return self.cache.get(key, {})
#         except Exception as e:
#             logger.error(f"Error getting cache value for {key}: {e}")
#             return {}

#     def find_keys_by_path(self, file_path: str) -> List[str]:
#         """Find all cache keys that reference a specific file path."""
#         matching_keys = []
#         normalized_path = os.path.normpath(file_path)
        
#         for key in self.cache.iterkeys():
#             value = self.get_value(key)
#             print("value",value)
#             # Check if the value contains our path
#             if isinstance(value, dict):
#                 # Check in metadata
#                 metadata = value.get('metadata', {})
#                 if metadata.get('file_path') == normalized_path:
#                     matching_keys.append(key)
#                     continue
                
#                 # Check in content
#                 content = value.get('value', {})
#                 if isinstance(content, dict):
#                     if str(normalized_path) in str(content):
#                         matching_keys.append(key)
#                         continue
            
#             # Check in raw value
#             if isinstance(value, str) and normalized_path in value:
#                 matching_keys.append(key)
        
#         return matching_keys
    
#     def remove_by_path(self, file_path: str) -> List[str]:
#         """Remove all cache entries related to a specific file path."""
#         keys_to_remove = self.find_keys_by_path(file_path)
#         removed_keys = []
        
#         for key in keys_to_remove:
#             print(key)
#             if self.remove_entry(key):
#                 removed_keys.append(key)
#                 logger.info(f"Removed cache entry: {key}")
        
#         if not removed_keys:
#             logger.info(f"No cache entries found for: {file_path}")
#         else:
#             logger.info(f"Removed {len(removed_keys)} cache entries for {file_path}")
        
#         return removed_keys
    
#     def get_stats(self) -> dict:
#         """Get cache statistics."""
#         return {
#             'size': len(self.cache),
#             'directory': str(self.cache_dir),
#             'entries': self.list_entries()
#         }
    
#     def clear_all(self) -> None:
#         """Clear entire cache."""
#         self.cache.clear()