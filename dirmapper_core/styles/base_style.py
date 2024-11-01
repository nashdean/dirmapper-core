from abc import ABC, abstractmethod
from typing import List, Tuple

class BaseStyle(ABC):
    """
    Abstract class for directory structure styles.
    """
    @abstractmethod
    def write_structure(self, structure: List[Tuple[str, int, str]], **kwargs) -> str:
        """
        Abstract method for writing the directory structure in a specific style.
        """
        pass
