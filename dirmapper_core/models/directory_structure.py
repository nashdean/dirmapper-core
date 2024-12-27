# dirmapper_core/models/directory_structure.py

from collections import defaultdict
import os
from typing import List, Dict, Optional, Union
from dirmapper_core.ignore.ignore_list_reader import IgnorePattern
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.utils.logger import logger
import hashlib
import json

class DirectoryStructure:
    """
    Class to represent a directory structure.
    """
    def __init__(self):
        self.description = None
        self.items: List[DirectoryItem] = []
        self._content_hash: Optional[str] = None

    @property
    def content_hash(self) -> str:
        """Calculate a hash of the directory structure's content."""
        if self._content_hash is None:
            # Sort items by path for consistent hashing
            sorted_items = sorted(self.items, key=lambda x: x.path)
            # Include metadata in hash calculation
            content = json.dumps([{
                'path': item.path,
                'level': item.level,
                'content_hash': item.content_hash,
                'metadata': item.metadata
            } for item in sorted_items], sort_keys=True)
            self._content_hash = hashlib.sha256(content.encode()).hexdigest()
        return self._content_hash

    def add_item(self, item: DirectoryItem):
        """Add an item and invalidate the content hash."""
        self.items.append(item)
        self._content_hash = None  # Invalidate hash when structure changes

    def get_level_hash(self, level: int) -> str:
        """Calculate a hash for a specific level in the directory structure."""
        level_items = [item for item in self.items if item.level == level]
        sorted_items = sorted(level_items, key=lambda x: x.path)
        content = json.dumps([{
            'path': item.path,
            'content_hash': item.content_hash,
            'metadata': item.metadata
        } for item in sorted_items], sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def to_list(self) -> List[DirectoryItem]:
        return self.items

    def get_item(self, path: str) -> Optional[DirectoryItem]:
        """
        Get a directory item by path. Supports both full and relative paths.
        Matches paths as strings without relying on OS path operations.

        Args:
            path (str): The path to search for (can be full path or just name)

        Returns:
            Optional[DirectoryItem]: The directory item if found, None otherwise.
        """
        # Try exact match first
        for item in self.items:
            if item.path == path:
                return item
                
        # Try basename match if exact match fails
        search_name = path.rstrip('/').split('/')[-1]  # Simple path splitting
        for item in self.items:
            item_name = item.path.rstrip('/').split('/')[-1]
            if item_name == search_name:
                return item
                
        return None
    
    def get_files(self, exclusions: Optional[Union[List[IgnorePattern], List[str]]] = None, inclusions: Optional[Union[List[IgnorePattern], List[str]]] = None) -> List[DirectoryItem]:
        """
        Get all items that are of type 'file', optionally excluding or including certain patterns.

        Args:
            exclusions (Optional[Union[List[IgnorePattern], List[str]]]): List of patterns or strings to exclude.
            inclusions (Optional[Union[List[IgnorePattern], List[str]]]): List of patterns or strings to include.

        Returns:
            List[DirectoryItem]: The file items.
        """
        try:
            if exclusions and all(isinstance(e, str) for e in exclusions):
                exclusions = [IgnorePattern(pattern=e) for e in exclusions]
            
            if inclusions and all(isinstance(i, str) for i in inclusions):
                inclusions = [IgnorePattern(pattern=i) for i in inclusions]

            files = [item for item in self.items if item.type == 'file']
            
            if exclusions:
                files = [item for item in files if not any(pattern.matches(item.path) for pattern in exclusions)]
            
            if inclusions:
                files = [item for item in files if any(pattern.matches(item.path) for pattern in inclusions)]
            
            return files
        except Exception as e:
            logger.error(f"Error in get_files: {e}")
            return []

    def get_directories(self) -> List[DirectoryItem]:
        """
        Get all items that are of type 'directory'.

        Returns:
            List[DirectoryItem]: The directory items.
        """
        return [item for item in self.items if item.type == 'directory']
    
    def get_items(self, level: int) -> List[DirectoryItem]:
        """
        Get all directory items at a specified level.
        
        Args:
            level (int): The level to get directory items from.
        
        Returns:
            List[DirectoryItem]: The directory items at the specified level.
        """
        return [item for item in self.items if item.level == level]
    
    def get_sub_items(self, path: str) -> List[DirectoryItem]:
        """
        Get all sub-items of a directory item by path.
        
        Args:
            path (str): The path of the directory item to get sub-items from.
        
        Returns:
            List[DirectoryItem]: The sub-items of the directory item.
        """
        return [item for item in self.items if path in item.path and item.path != path]
    
    def get_item_names(self, level: int = -1) -> List[str]:
        """
        Get the names of all directory items at a specified level. If level is -1, return all items.
        
        Args:
            level (int): The level to get directory item names from.
        
        Returns:
            List[str]: The names of the directory items at the specified level.
        """
        if level == -1:
            return [item.name for item in self.items]
        return [item.name for item in self.get_items(level)]
    
    def get_item_paths(self, level: int = -1) -> List[str]:
        """
        Get the paths of all directory items at a specified level. If level is -1, return all items.
        
        Args:
            level (int): The level to get directory item paths from.
            
        Returns:
            List[str]: The paths of the directory items at the specified level.
        """
        if level == -1:
            return [item.path for item in self.items]
        return [item.path for item in self.get_items(level)]
    
    def get_item_metadata(self, level: int = -1) -> List[Dict]:
        """
        Get the metadata of all directory items at a specified level. If level is -1, return all items.
        
        Args:
            level (int): The level to get directory item metadata from.
            
        Returns:
            List[Dict]: The metadata of the directory items at the specified level.
        """
        if level == -1:
            return [item.metadata for item in self.items]
        return [item.metadata for item in self.get_items(level)]

    def to_dict(self) -> Dict:
        """
        Convert the structure to a dictionary format with levels as keys and lists of DirectoryItem as values.

        Returns:
            Dict[int, List[DirectoryItem]]: The directory structure as a dictionary.
        """
        structure_dict = defaultdict(list)
        for item in self.items:
            structure_dict[item.level].append(item)
        return dict(structure_dict)
    
    #TODO: There is a bug where not all items are added from the nested dictionary back into the DirectoryStructure
    def merge_nested_dict(self, nested_dict: dict) -> None:
        """
        Merge a nested dictionary with __keys__ back into the DirectoryStructure.
        Updates existing items with non-null values from the nested dictionary.
        
        Args:
            nested_dict (dict): Nested dictionary with __keys__ containing metadata
        """
        def process_dict(current_dict: dict, current_path: str = "") -> None:
            for key, value in current_dict.items():
                if not isinstance(value, dict):
                    continue
                    
                # Build the full path for this item
                path = os.path.join(current_path, key) if current_path else key

                # If this dict has __keys__, update the corresponding DirectoryItem
                if '__keys__' in value:
                    item = self.get_item(path)

                    if item:
                        keys_dict = value['__keys__']
                        
                        # Update type if present
                        if 'type' in keys_dict and keys_dict['type'] is not None:
                            item.metadata['type'] = keys_dict['type']

                        # Update content if present
                        if 'content' in keys_dict and keys_dict['content'] is not None:
                            item.metadata['content'] = keys_dict['content']

                        # Update summary if present
                        if 'summary' in keys_dict and keys_dict['summary'] is not None:
                            item.metadata['summary'] = keys_dict['summary']

                        # Update short_summary if present
                        if 'short_summary' in keys_dict and keys_dict['short_summary'] is not None:
                            item.metadata['short_summary'] = keys_dict['short_summary']

                        # Update tags if present
                        if 'tags' in keys_dict and keys_dict['tags'] is not None:
                            item.metadata['tags'] = keys_dict['tags']
                
                # Recursively process nested dictionaries
                process_dict(value, path)
        
        # Start processing from root
        process_dict(nested_dict)

    def to_nested_dict(self, metadata_fields: Optional[List[str]] = None, use_json_style: bool = False) -> Dict[str, Union[Dict, None]]:
        """
        Convert the structure to a nested dictionary format with metadata under __keys__.
        
        Args:
            metadata_fields (Optional[List[str]]): List of metadata fields to include.
                If None, include all metadata fields.
                If empty list, set __keys__ to None.
            use_json_style (bool): If True, uses JSONStyle's richer structure.
                If False, uses the simpler legacy format for backward compatibility.
                
        Returns:
            Dict[str, Union[Dict, None]]: The directory structure as a nested dictionary.
        """
        if use_json_style:
            from dirmapper_core.styles.json_style import JSONStyle
            return JSONStyle.write_structure(self)

        # Legacy format
        nested_dict = {}

        for item in self.items:
            parts = item.path.split(os.sep)
            current_level = nested_dict

            # Navigate to the correct level
            for part in parts[:-1]:
                if part:  # Skip empty parts
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]

            # Add the final item with its metadata
            if parts[-1]:  # Only process non-empty parts
                current_level[parts[-1]] = {}
                
                # Handle metadata
                if metadata_fields == []:
                    current_level[parts[-1]]['__keys__'] = None
                else:
                    # If metadata_fields is None, include all fields
                    fields_to_include = metadata_fields or item.metadata.keys()
                    metadata = {
                        k: v for k, v in item.metadata.items() 
                        if k in fields_to_include
                    }
                    if metadata:
                        current_level[parts[-1]]['__keys__'] = metadata

        return nested_dict
    
    def print(self) -> str:
        """
        Print the directory structure to the console.    
        """
        for item in self.items:
            print(item)

    def __repr__(self):
        return f"DirectoryStructure(items={self.items})"
    
    def __str__(self):
        return self.__repr__()
    
    def __len__(self):
        return len(self.items)