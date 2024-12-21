# dirmapper_core/models/directory_item.py

import hashlib
import os
from typing import List, Optional, Dict

from dirmapper_core.utils.logger import logger

class DirectoryItem:
    """
    Class to represent a directory item in a directory structure.
    """
    def __init__(self, path: str, level: int, name: str, metadata: Optional[Dict] = None):
        self.path = path
        self.level = level
        self.name = name
        self.metadata = metadata or {'type': None, 'content': None, 'summary': None, 'short_summary': None, 'tags': []}

        self._init_empty_metadata()

        self._content = None  # Private attribute to store the content

    @property
    def type(self) -> str:
        """Get the type of the directory item."""
        return self.metadata.get('type', 'file' if os.path.isfile(self.path) else 'directory')
    
    @type.setter
    def type(self, value: str) -> None:
        """Set the type of the directory item."""
        if value not in ['file', 'directory']:
            raise ValueError("Type must be either 'file' or 'directory'")
        self.metadata['type'] = value

    @property 
    def summary(self) -> Optional[str]:
        """Get the summary of the directory item."""
        return self.metadata.get('summary')
    
    @summary.setter
    def summary(self, value: Optional[str]) -> None:
        """Set the summary of the directory item."""
        self.metadata['summary'] = value

    @property
    def short_summary(self) -> Optional[str]:
        """Get the short summary of the directory item."""
        return self.metadata.get('short_summary')
    
    @short_summary.setter
    def short_summary(self, value: Optional[str]) -> None:
        """Set the short summary of the directory item."""
        self.metadata['short_summary'] = value

    @property
    def tags(self) -> List[str]:
        """Get the tags of the directory item."""
        return self.metadata.get('tags', [])
    
    @tags.setter
    def tags(self, value: List[str]) -> None:
        """Set the tags of the directory item."""
        if not isinstance(value, list):
            raise ValueError("Tags must be a list")
        self.metadata['tags'] = value
    
    @property
    def content_hash(self) -> Optional[str]:
        """Get the content hash of the directory item."""
        return self.metadata.get('content_hash')

    @content_hash.setter
    def content_hash(self, value: Optional[str]) -> None:
        """Set the content hash of the directory item."""
        self.metadata['content_hash'] = value
        
    @property
    def content(self) -> Optional[str]:
        """
        Get the content of the directory item.
        Returns hardcoded content from metadata if available, otherwise attempts to load from file.
        """
        # First check for hardcoded content in metadata
        if self.metadata.get('content') is not None:
            return self.metadata['content']
        
        # Lazy load content from file if not already loaded and content is not hardcoded
        if self._content is None and 'content' in self.metadata:
            try:
                with open(self.path, 'r') as f:
                    self._content = f.read()
                    self.content_hash = self._hash_content(self._content)  # Update hash
            except Exception as e:
                self._content = None
                logger.error(f"Failed to read content from {self.path}: {e}")
        return self._content

    def _hash_content(self, content: str) -> str:
        """Compute a hash of the content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def __repr__(self):
        return f"DirectoryItem(path={self.path}, level={self.level}, name={self.name}, metadata={self.metadata})"
    
    def __str__(self):
        return "{}, {}, {}, {}".format(self.path, self.level, self.name, self.metadata)
    
    def _init_empty_metadata(self):
        """
        Initialize empty metadata fields if they are None.
        """
        if not self.metadata.get('type'):
            self.metadata['type'] = 'file' if os.path.isfile(self.path) else 'directory'
        if not self.metadata.get('summary'):
            self.metadata['summary'] = None
        if not self.metadata.get('content'):
            self.metadata['content'] = None
        if not self.metadata.get('short_summary'):
            self.metadata['short_summary'] = None
        if not self.metadata.get('tags'):
            self.metadata['tags'] = []
                          
    def print(self) -> str:
        """
        Print the directory item to the console.
        """
        return str(self)
    
    def to_dict(self) -> Dict:
        """
        Convert the directory item to a dictionary.
        
        Returns:
            Dict: The directory item as a dictionary.
        """
        return {
            'path': self.path,
            'level': self.level,
            'name': self.name,
            'metadata': self.metadata
        }
    
    def to_tuple(self) -> tuple:
        """
        Convert the directory item to a tuple.
        
        Returns:
            tuple: The directory item as a tuple.
        """
        return self.path, self.level, self.name, self.metadata