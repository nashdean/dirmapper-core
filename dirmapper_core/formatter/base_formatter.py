from abc import ABC, abstractmethod
from dirmapper_core.models.directory_structure import DirectoryStructure

class BaseFormatter(ABC):
    """
    Abstract base class for formatters. Formatters are responsible for converting data 
    into a specific format (e.g., plain text, HTML, JSON, etc.).
    """
    @abstractmethod
    def format(self, data: DirectoryStructure, instructions: dict = None) -> str | dict:
        """
        Abstract method to format the data into a specific format.
        
        Args:
            data: The Directory Structure object to format
            instructions: Dictionary containing formatting instructions
            
        Returns:
            Formatted output as string or dictionary
        """
        pass
