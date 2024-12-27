from typing import List
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.utils.logger import logger
from dirmapper_core.ai.content_generator import ContentGenerator

class ContentService:
    """
    Service class to handle content generation requests.
    Separates content generation logic from style implementations.
    """
    _instance = None
    _generator = None

    @classmethod
    def initialize(cls, api_key: str = None):
        """Initialize the content service with an API key."""
        if api_key and not cls._generator:
            cls._generator = ContentGenerator(api_key)

    @classmethod
    def generate_file_content(cls, path: str, directory_structure: DirectoryStructure) -> str:
        """
        Generate content for a file using the content generator if available.
        
        Args:
            path: Path to the file
            directory_structure: The directory structure providing context
            
        Returns:
            Generated content or empty string if generation fails/unavailable
        """
        if not cls._generator:
            logger.warning("Content generator not initialized. Call ContentService.initialize() with an API key first.")
            return ""
            
        try:
            return cls._generator.generate_file_content(path, directory_structure)
        except Exception as e:
            logger.error(f"Error generating content for {path}: {str(e)}")
            return ""
