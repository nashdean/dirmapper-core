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

    def write_structure(self, safety_check: bool = True):
        """
        Write the directory structure to the file system, if base_path is set.

        Args:
            safety_check (bool): Flag indicating whether to prompt the user before writing to the file system. Defaults to True.
        """
        if not self.base_path:
            raise ValueError("Base path not set. Cannot write to file system.")
        if safety_check:
            logger.warning(f"Safety is enabled. You are about to create directories and files on the file system and may overwrite directories/files of the same name at the `{os.path.abspath(self.base_path)}` path. Please ensure you have the correct permissions.")
            response = input("Do you want to continue? (y/n): ")
            if response.lower() != 'y':
                logger.info("Aborting operation.")
                return False
        logger.info(f"Creating directory structure at root directory: {os.path.abspath(self.base_path)}")
        return self._write_to_filesystem(self.base_path, self.template)

    def _write_to_filesystem(self, base_path: str, structure: dict) -> bool:
        """
        Recursively write the structure to the file system. Helper method for create_structure.

        Args:
            base_path (str): The base path to create the directory structure.
            structure (dict): The directory structure template to create.
        
        Returns:
            bool: True if the directory structure was created successfully, False otherwise.
        Example:
            Parameters:
                base_path = '/path/to/base'
                structure = {
                    "dir1/": {
                        "file1.txt": {},
                        "file2.txt": {},
                        "subdir1/": {
                            "file3.txt": {}
                        }
                    },
                    "dir2/": {
                        "file4.txt": {},
                        "file5.txt": {},
                        "subdir2/": {
                            "file6.txt": {}
                        }
                    }
                }
            Result:
                # Directory structure created at /path/to/base
                /path/to/base
                ├── dir1
                │   ├── file1.txt
                │   ├── file2.txt
                │   └── subdir1
                │       └── file3.txt
                └── dir2
                    ├── file4.txt
                    ├── file5.txt
                    └── subdir2
                        └── file6.txt
        """
        try:
            for name, content in structure.items():
                # Remove trailing slash for the actual path
                path = os.path.join(base_path, name.rstrip('/'))

                if name.endswith('/'):
                    # It's a directory
                    os.makedirs(path, exist_ok=True)
                    logger.debug(f"Created directory: {path}")
                    # Recursively write the contents of the directory
                    self._write_to_filesystem(path, content)
                else:
                    # It's a file
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, 'w') as f:
                        f.write('')  # Create an empty file
                    logger.debug(f"Created file: {path}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory structure: {e}")
            return False

