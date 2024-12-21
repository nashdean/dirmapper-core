import os
from collections import defaultdict
from typing import List, Dict
from dirmapper_core.ignore.ignore_list_reader import IgnorePattern

class PathIgnorer:
    """
    Class to manage path ignoring based on a list of ignore patterns.
    
    Attributes:
        ignore_patterns (List[IgnorePattern]): A list of IgnorePattern objects for paths to ignore.
        ignore_counts (defaultdict): A dictionary to keep track of ignored paths per directory.
    """
    def __init__(self, ignore_list: List[IgnorePattern] = []):
        """
        Initialize the PathIgnorer with a list of ignore patterns.
        
        Args:
            ignore_list (List[IgnorePattern]): The list of patterns to ignore.
        """
        self.ignore_patterns = ignore_list
        self.ignore_counts = defaultdict(int)

    def should_ignore(self, path: str) -> bool:
        """
        Check if a given path should be ignored.
        
        Args:
            path (str): The path to check.
        
        Returns:
            bool: True if the path should be ignored, False otherwise.
        """
        for pattern in self.ignore_patterns:
            if pattern.matches(path):
                self._increment_ignore_count(path)
                return True
        return False

    def _increment_ignore_count(self, path: str) -> None:
        """
        Increment the count of ignored paths for a specific directory.
        
        Args:
            path (str): The path that was ignored.
        """
        directory = os.path.dirname(path)
        self.ignore_counts[directory] += 1

    def get_ignore_counts(self) -> Dict[str, int]:
        """
        Get the count of ignored paths per directory.
        
        Returns:
            Dict[str, int]: A dictionary with directories as keys and ignore counts as values.
        """
        return self.ignore_counts
