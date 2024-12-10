# dirmapper_core/models/directory_item.py

from typing import Optional, Dict

from dirmapper_core.utils import logger

class DirectoryItem:
    """
    Class to represent a directory item in a directory structure.
    """
    def __init__(self, path: str, level: int, name: str, metadata: Optional[Dict] = None):
        self.path = path
        self.level = level
        self.name = name
        self.metadata = metadata or {'summary': None, 'content': None, 'short_summary': None, 'tags': []}

        self._init_empty_metadata()

        self._content = None  # Private attribute to store the content

    @property
    def content(self) -> Optional[str]:
        """
        Get the content of the directory item.
        """
        if self._content is None and 'content' in self.metadata:
            try:
                with open(self.path, 'r') as f:
                    self._content = f.read()
            except Exception as e:
                self._content = None
                logger.error(f"Failed to read content from {self.path}: {e}")
        return self._content

    def __repr__(self):
        return f"DirectoryItem(path={self.path}, level={self.level}, name={self.name}, metadata={self.metadata})"
    
    def __str__(self):
        return "{}, {}, {}, {}".format(self.path, self.level, self.name, self.metadata)
    
    def _init_empty_metadata(self):
        """
        Initialize empty metadata fields if they are None.
        """
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