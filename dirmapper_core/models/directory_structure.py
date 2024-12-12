# dirmapper_core/models/directory_structure.py

from collections import defaultdict
import os
from typing import List, Dict, Optional, Union
from dirmapper_core.models.directory_item import DirectoryItem

class DirectoryStructure:
    """
    Class to represent a directory structure.
    """
    def __init__(self):
        self.items: List[DirectoryItem] = []

    def add_item(self, item: DirectoryItem):
        self.items.append(item)

    def to_list(self) -> List[DirectoryItem]:
        return self.items

    def get_item(self, path: str) -> Optional[DirectoryItem]:
        """
        Get a directory item by path.

        Args:
            path (str): The path of the directory item to get.

        Returns:
            Optional[DirectoryItem]: The directory item if found, None otherwise.
        """
        for item in self.items:
            if item.path == path:
                return item
        return None
    
    def get_items(self, level: int) -> List[DirectoryItem]:
        """
        Get all directory items at a specified level.
        
        Args:
            level (int): The level to get directory items from.
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
    
    def to_nested_dict(self, metadata_fields: Optional[List[str]] = None) -> Dict[str, Union[Dict, None]]:
        """
        Convert the structure to a nested dictionary format with metadata under __keys__.
        
        Args:
            metadata_fields (Optional[List[str]]): List of metadata fields to include.
                If None, include all metadata fields.
                If empty list, set __keys__ to None.
                
        Returns:
            Dict[str, Union[Dict, None]]: The directory structure as a nested dictionary.
        
        Example:
            {
                "folder1": {
                    "file1.txt": {
                        "size": "1.2MB",
                        "date_modified": "2021-01-01"
                    },
                    "file2.txt": {
                        "size": "1.5MB",
                        "date_modified": "2021-01-02"
                    }
                },
                "folder2": {
                    "file3.txt": {
                        "size": "1.8MB",
                        "date_modified": "2021-01-03"
                    }
                }
            }
        """
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