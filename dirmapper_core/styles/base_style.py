from abc import ABC, abstractmethod
from typing import List, Tuple

class BaseStyle(ABC):
    """
    Abstract class for directory structure styles.
    """
    @abstractmethod
    def write_structure(structure: List[Tuple[str, int, str]], **kwargs) -> str:
        """
        Abstract method for writing the directory structure in a specific style.
        """
        pass
    @abstractmethod
    def parse_from_style(structure: dict | str, root_dir: str = "") -> List[Tuple[str, int, str]]:
        """
        Abstract method for parsing the directory structure from a specific style back into the common List of tuples.
        """
        pass