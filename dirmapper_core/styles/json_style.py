from datetime import datetime
import os
import platform
from typing import List, Tuple
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.styles.base_style import BaseStyle

# Import Unix-specific modules only on Unix systems
if platform.system() != "Windows":
    import pwd
    import grp

class JSONStyle(BaseStyle):
    """
    JSONStyle is a concrete class that inherits from the BaseStyle class. It provides an implementation for the write_structure method that converts a directory structure into a JSON representation.
    """
    #TODO: Update this to accept kwarg generate_content to generate file content based on the file name and context of the directory and intended project.
    @staticmethod
    def write_structure(structure: DirectoryStructure, **kwargs) -> dict:
        """
        Converts a DirectoryStructure object into a JSON-like representation.
        Each file or directory includes a "__keys__" field containing metadata and placeholders for content.

        Args:
            structure (DirectoryStructure): The directory structure to convert.
            **kwargs:
                root_dir (str): The root directory path (optional, if not provided uses the first item's path).
                include_content (bool): If True, attempt to load file content from the file system.
                generate_content (bool): If True, attempt to generate file content via OpenAI if no existing content is found.

        Returns:
            dict: A JSON representation of the directory structure with metadata.
        """
        root_dir = kwargs.get('root_dir')
        include_content = kwargs.get('include_content', False)
        generate_content = kwargs.get('generate_content', False)

        items = structure.to_list()
        if not items:
            return {}

        # The first item should be the root directory
        root_item = items[0]
        if root_item.level != 0:
            raise ValueError("The first item in the structure must be the root directory with level 0.")
        if not root_dir:
            root_dir = root_item.path

        # Get metadata for the root directory
        root_metadata = JSONStyle.get_metadata(root_item.path, True, root_dir)
        root_dict = {
            "__keys__": {
                "meta": root_metadata,
                "content": {
                    "content_summary": root_item.metadata.get("summary"),
                    "short_summary": root_item.metadata.get("short_summary")
                }
            }
        }

        # We'll insert all subsequent items into root_dict
        # The top-level dictionary will have one key: the absolute root path + '/'
        nested_dict = {
            f"{root_dir}/": root_dict
        }

        # Process all items except the first (root) one
        for item in items[1:]:
            is_dir = os.path.isdir(item.path)
            metadata = JSONStyle.get_metadata(item.path, is_dir, root_dir)

            # Compute relative path from root
            relative_path = os.path.relpath(item.path, start=root_dir)
            parts = relative_path.split(os.sep)

            # Navigate under the root directory key
            current = root_dict
            for part in parts[:-1]:
                dir_key = part + '/'
                if dir_key not in current:
                    # Create a placeholder for intermediate directories without __keys__
                    mid_path = os.path.join(root_dir, *parts[:parts.index(part)+1])
                    mid_meta = JSONStyle.get_metadata(mid_path, True, root_dir)
                    current[dir_key] = {
                        "__keys__": {
                            "meta": mid_meta,
                            "content": {
                                "content_summary": None,
                                "short_summary": None
                            }
                        }
                    }
                current = current[dir_key]

            # Handle the last part
            last_part = parts[-1]
            if is_dir:
                folder_key = last_part + '/'
                current[folder_key] = {
                    "__keys__": {
                        "meta": metadata,
                        "content": {
                            "content_summary": item.metadata.get("summary"),
                            "short_summary": item.metadata.get("short_summary")
                        }
                    }
                }
            else:
                # It's a file
                content = None
                if include_content:
                    content = item.content  # Triggers lazy loading from DirectoryItem
                    if content is None and generate_content:
                        content = JSONStyle.generate_file_content(item.path, items, root_dir)

                current[last_part] = {
                    "__keys__": {
                        "meta": metadata,
                        "content": {
                            "file_content": content,
                            "content_summary": item.metadata.get("summary"),
                            "short_summary": item.metadata.get("short_summary")
                        }
                    }
                }

        return nested_dict
    
    def get_metadata(path: str, is_dir: bool, root_path: str) -> dict:
        """
        Retrieves real metadata for a given file or directory path.
        """
        try:
            stats = os.stat(path)

            # Metadata values
            creation_date = datetime.fromtimestamp(stats.st_ctime).isoformat()
            last_modified = datetime.fromtimestamp(stats.st_mtime).isoformat()
            size = stats.st_size if not is_dir else 0  # Size for files only

            # Cross-platform handling for author and last modified by
            if platform.system() == "Windows":
                author = os.getlogin()  # Fallback to current user on Windows
                last_modified_by = "unknown"  # Group info not available on Windows
            else:
                # Use Unix-specific modules for author and group
                author = pwd.getpwuid(stats.st_uid).pw_name
                last_modified_by = grp.getgrgid(stats.st_gid).gr_name

            # Calculate relative path from the root directory
            relative_path = os.path.relpath(path, start=root_path)

            return {
                "type": "directory" if is_dir else "file",
                "relative_path": relative_path,
                "creation_date": creation_date,
                "last_modified": last_modified,
                "author": author,
                "last_modified_by": last_modified_by,
                "size": size
            }
        except PermissionError:
            return {
                "type": "directory" if is_dir else "file",
                "relative_path": os.path.relpath(path, start=root_path),
                "creation_date": "permission_denied",
                "last_modified": "permission_denied",
                "author": "permission_denied",
                "last_modified_by": "permission_denied",
                "size": 0
            }
        except FileNotFoundError:
            return {
                "type": "directory" if is_dir else "file",
                "relative_path": os.path.relpath(path, start=root_path),
                "creation_date": "unknown",
                "last_modified": "unknown",
                "author": "unknown",
                "last_modified_by": "unknown",
                "size": 0
            }
    
    @staticmethod
    def parse_from_style(json_dict: dict) -> DirectoryStructure:
        """
        Converts a JSON/dict representation of a directory structure back into a DirectoryStructure object.

        Args:
            json_dict (dict): The JSON/dict representation of the directory structure.

        Returns:
            DirectoryStructure: The parsed directory structure as a DirectoryStructure object.
        """
        structure = DirectoryStructure()
        
        # The root directory should be the first key
        # It should end with '/' if it's a directory
        root_key = next(iter(json_dict))
        if not root_key.endswith('/'):
            raise ValueError("Invalid JSON structure: root key must represent a directory and end with '/'.")
        
        # Extract the root path
        root_path = root_key.rstrip('/')
        root_obj = json_dict[root_key]

        # Extract root metadata from __keys__
        root_keys = root_obj.get("__keys__", {})
        root_meta = root_keys.get("meta", {})
        root_item = DirectoryItem(path=root_path, level=0, name=root_path, metadata=root_meta)
        structure.add_item(root_item)

        # Remove __keys__ so we can parse the contents
        if "__keys__" in root_obj:
            del root_obj["__keys__"]

        # Recursively parse the structure
        structure.items.extend(JSONStyle._traverse_json(root_obj, level=1, parent_path=root_path))

        return structure

    @staticmethod
    def _traverse_json(node: dict, level: int, parent_path: str) -> List[DirectoryItem]:
        """
        Recursively traverses the JSON/dict structure to build the list of DirectoryItem objects.
        
        Args:
            node (dict): The current dictionary node representing files/directories.
            level (int): The current level in the directory hierarchy.
            parent_path (str): The absolute path to the parent directory.

        Returns:
            List[DirectoryItem]: A list of DirectoryItem objects.
        """
        structure = []
        for key, value in node.items():
            if key == '__keys__':
                # Already handled at higher level, skip
                continue

            is_dir = key.endswith('/')
            item_name = key.rstrip('/')
            item_path = os.path.join(parent_path, item_name)

            # Extract __keys__ if present
            item_keys = {}
            item_meta = {}
            if isinstance(value, dict) and "__keys__" in value:
                item_keys = value["__keys__"]
                item_meta = item_keys.get("meta", {})
            
            item = DirectoryItem(path=item_path, level=level, name=item_name, metadata=item_meta)
            structure.append(item)

            if is_dir:
                # It's a directory, recurse deeper
                sub_node = value.copy()
                if "__keys__" in sub_node:
                    del sub_node["__keys__"]
                structure.extend(JSONStyle._traverse_json(sub_node, level + 1, item_path))

        return structure
    
    @staticmethod
    def generate_file_content(path: str, items: List[DirectoryItem], root_dir: str) -> str:
        """
        Generate file content using the ContentService.
        
        Args:
            path: Path to the file
            items: List of directory items for context
            root_dir: Root directory path
            
        Returns:
            Generated content or empty string if generation fails
        """
        from dirmapper_core.ai.content_service import ContentService
        from dirmapper_core.models.directory_structure import DirectoryStructure
        
        # Create DirectoryStructure from items
        structure = DirectoryStructure()
        for item in items:
            structure.add_item(item)
            
        return ContentService.generate_file_content(path, structure)


