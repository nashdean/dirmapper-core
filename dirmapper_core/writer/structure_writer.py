import os
from typing import Optional
from dirmapper_core.utils.logger import logger

class StructureWriter:
    """
    Class to create directory structures from a template.
    """
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the StructureWriter object.

        Args:
            base_path (str): The base path to create the directory structure.
        """
        self.base_path = os.path.expanduser(base_path) if base_path else None
        self.meta = {}
        self.structure = {}

    def create_structure(self, structure: dict):
        """
        Store the directory structure from the template.

        Args:
            structure (dict): The directory structure template to create.
        """
        if 'meta' not in structure or 'template' not in structure:
            raise ValueError("Template must contain 'meta' and 'template' sections.")
        
        self.meta = structure['meta']
        self.template = structure['template']

        if 'version' not in self.meta or self.meta['version'] != '1.1':
            raise ValueError("Unsupported template version. Supported version is '1.1'.")
        
        # Log or use additional meta tags if needed
        author = self.meta.get('author', 'Unknown')
        source = self.meta.get('source', 'Unknown')
        description = self.meta.get('description', 'No description provided')
        creation_date = self.meta.get('creation_date', 'Unknown')
        last_modified = self.meta.get('last_modified', 'Unknown')
        license = self.meta.get('license', 'No license specified')

        logger.info(f"Template by author, {author}")
        logger.info(f"Template source, {source}")
        logger.debug(f"Template Description: {description}")
        logger.debug(f"Template Creation date: {creation_date}")
        logger.info(f"Template Last modified: {last_modified}")
        logger.debug(f"Template License: {license}")

    def write_structure(self):
        """
        Write the directory structure to the file system, if base_path is set.
        """
        if not self.base_path:
            raise ValueError("Base path not set. Cannot write to file system.")
        logger.info(f"Creating directory structure at root directory: {os.path.abspath(self.base_path)}")
        self._write_to_filesystem(self.base_path, self.template)

    def _write_to_filesystem(self, base_path: str, structure: dict):
        """
        Recursively write the structure to the file system. Helper method for create_structure.

        Args:
            base_path (str): The base path to create the directory structure.
            structure (dict): The directory structure template to create.
        """
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            if isinstance(content, list):
                os.makedirs(path, exist_ok=True)
                for item in content:
                    if isinstance(item, dict):
                        self._write_to_filesystem(path, item)
            else:
                # Ensure the directory exists before creating the file
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write('')  # Create an empty file
