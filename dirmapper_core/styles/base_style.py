from abc import ABC, abstractmethod
from typing import List, Tuple

from dirmapper_core.models.directory_structure import DirectoryStructure

class BaseStyle(ABC):
    """
    Abstract class for directory structure styles.
    """
    @abstractmethod
    def write_structure(structure: DirectoryStructure, **kwargs) -> str:
        """
        Abstract method for writing the directory structure in a specific style.
        """
        pass
    @abstractmethod
    def parse_from_style(structure: dict | str) -> DirectoryStructure:
        """
        Abstract method for parsing the directory structure from a specific style back into the common DirectoryStructure object.
        """
        pass