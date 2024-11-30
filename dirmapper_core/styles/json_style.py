from datetime import datetime
import os
import platform
from typing import List, Tuple
from dirmapper_core.styles.base_style import BaseStyle

# Import Unix-specific modules only on Unix systems
if platform.system() != "Windows":
    import pwd
    import grp

class JSONStyle(BaseStyle):
    """
    JSONStyle is a concrete class that inherits from the BaseStyle class. It provides an implementation for the write_structure method that converts a directory structure into a JSON representation.
    """
    @staticmethod
    def write_structure(structure: List[Tuple[str, int, str]], **kwargs) -> dict:
        """
        Converts a list of tuples representing a directory structure into a JSON-like representation. 
        Each file or directory includes a "__keys__" field containing metadata (e.g., type, size, 
        creation date, last modified date, author, and last modified by) and placeholders for content summaries.

        The function handles cross-platform compatibility (Windows and Unix) and gracefully manages permission 
        errors or missing files.

        Args:
            - structure (List[Tuple[str, int, str]]): A list of tuples where each tuple contains:
                - str: The path to the file or directory.
                - int: The level of indentation in the hierarchy.
                - str: The name of the file or directory.
        
        Returns:
            - dict: A JSON representation of the directory structure with metadata.

        Example:
            Input structure:
                [
                    ('/path/to/dir', 0, 'dir'),
                    ('/path/to/dir/file1.txt', 1, 'file1.txt'),
                    ('/path/to/dir/subdir', 1, 'subdir'),
                    ('/path/to/dir/subdir/file2.txt', 2, 'file2.txt')
                ]

            Output structure:
                {
                    '/path/to/dir': {
                        '__keys__': {
                            'meta': {
                                'type': 'folder',
                                'relative_path': 'dir',
                                'creation_date': '2024-11-26T21:30:00.000000',
                                'last_modified': '2024-11-26T21:35:00.000000',
                                'author': 'user',
                                'last_modified_by': 'developers',
                                'size': 0
                            },
                            'content': {
                                'content_summary': 'none',
                                'short_summary': 'none'
                            }
                        },
                        'file1.txt': {
                            '__keys__': {
                                'meta': {
                                    'type': 'file',
                                    'relative_path': 'file1.txt',
                                    'creation_date': '2024-11-26T21:30:00.000000',
                                    'last_modified': '2024-11-26T21:35:00.000000',
                                    'author': 'user',
                                    'last_modified_by': 'developers',
                                    'size': 1024
                                },
                                'content': {
                                    'file_content': 'none',
                                    'content_summary': 'none',
                                    'short_summary': 'none'
                                }
                            }
                        },
                        'subdir/': {
                            '__keys__': {
                                'meta': {
                                    'type': 'folder',
                                    'relative_path': 'subdir',
                                    'creation_date': '2024-11-26T21:30:00.000000',
                                    'last_modified': '2024-11-26T21:35:00.000000',
                                    'author': 'user',
                                    'last_modified_by': 'developers',
                                    'size': 0
                                },
                                'content': {
                                    'content_summary': 'none',
                                    'short_summary': 'none'
                                }
                            },
                            'file2.txt': {
                                '__keys__': {
                                    'meta': {
                                        'type': 'file',
                                        'relative_path': 'subdir/file2.txt',
                                        'creation_date': '2024-11-26T21:30:00.000000',
                                        'last_modified': '2024-11-26T21:35:00.000000',
                                        'author': 'user',
                                        'last_modified_by': 'developers',
                                        'size': 2048
                                    },
                                    'content': {
                                        'file_content': 'none',
                                        'content_summary': 'none',
                                        'short_summary': 'none'
                                    }
                                }
                            }
                        }
                    }
                }
        """
        def get_metadata(path: str, is_dir: bool) -> dict:
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

                return {
                    "type": "folder" if is_dir else "file",
                    "relative_path": os.path.relpath(path),
                    "creation_date": creation_date,
                    "last_modified": last_modified,
                    "author": author,
                    "last_modified_by": last_modified_by,
                    "size": size
                }
            except PermissionError:
                # Handle lack of permissions gracefully
                return {
                    "type": "folder" if is_dir else "file",
                    "relative_path": os.path.relpath(path),
                    "creation_date": "permission_denied",
                    "last_modified": "permission_denied",
                    "author": "permission_denied",
                    "last_modified_by": "permission_denied",
                    "size": 0
                }
            except FileNotFoundError:
                # Handle case where file/directory doesn't exist
                return {
                    "type": "folder" if is_dir else "file",
                    "relative_path": os.path.relpath(path),
                    "creation_date": "unknown",
                    "last_modified": "unknown",
                    "author": "unknown",
                    "last_modified_by": "unknown",
                    "size": 0
                }
            
        def build_json_structure(structure, start_index: int, current_level: int, parent_path: str) -> Tuple[dict, int]:
            """
            Builds the modified JSON-like structure with real metadata.
            """
            result = {}
            i = start_index
            while i < len(structure):
                item_path, item_level, item_name = structure[i]
                if item_level < current_level:
                    # We've moved back to a higher level; return to the previous call
                    break

                # Construct the full path to the item
                full_item_path = os.path.join(parent_path, item_name)

                # Determine if item is a directory based on the next item's level
                if (i + 1) < len(structure) and structure[i + 1][1] > item_level:
                    is_dir = True
                else:
                    is_dir = False

                metadata = get_metadata(full_item_path, is_dir)

                if is_dir:
                    # Recursively build the sub-structure
                    sub_structure, new_index = build_json_structure(structure, i + 1, item_level + 1, full_item_path)
                    # Append '/' to directory names for consistency
                    folder_key = item_name + '/'
                    result[folder_key] = {
                        "__keys__": {
                            "meta": metadata,
                            "content": {
                                "content_summary": None,
                                "short_summary": None
                            }
                        },
                        **sub_structure
                    }
                    i = new_index  # Update index to the position returned by recursion
                else:
                    result[item_name] = {
                        "__keys__": {
                            "meta": metadata,
                            "content": {
                                "file_content": None,
                                "content_summary": None,
                                "short_summary": None
                            }
                        }
                    }
                    i += 1  # Move to the next item

            return result, i
        
        # Start building the structure at level root_level + 1
        root_path, root_level, root_name = structure[0]
        json_structure, _ = build_json_structure(structure, 1, root_level + 1, root_path)

        # Include metadata for the root directory and attach its contents
        return {
            root_name + '/': {
                "__keys__": {
                    "meta": get_metadata(root_path, is_dir=True),
                    "content": {
                        "content_summary": None,
                        "short_summary": None
                    }
                },
                **json_structure
            }
        }
    
    @staticmethod
    def parse_from_style(json_dict: dict) -> List[Tuple[str, int, str]]:
        """
        Converts a JSON/dict representation of a directory structure back into a list of tuples.
        
        Each tuple contains:
            - str: The path to the file or directory.
            - int: The level of indentation in the hierarchy.
            - str: The name of the file or directory.

        Args:
            json_dict (Dict): The JSON/dict representation of the directory structure.

        Returns:
            List[Tuple[str, int, str]]: A list of tuples representing the directory structure.
        """
        # Initialize the structure list
        structure = []

        # Get the root key and its value
        root_key = next(iter(json_dict))
        root_value = json_dict[root_key]

        # Root item
        root_name = root_key.rstrip('/')
        root_path = root_name  # For root, path is the name itself
        structure.append((root_path, 0, root_path))

        # Traverse the root_value
        structure.extend(JSONStyle._traverse_json(root_value, level=1, parent_path=""))

        return structure

    def _traverse_json(node: dict, level: int, parent_path: str) -> List[Tuple[str, int, str]]:
        """
        Recursively traverses the JSON/dict structure to build the list of tuples.

        Args:
            node (Dict): The current node in the JSON/dict structure.
            level (int): The current level in the directory hierarchy.
            parent_path (str): The path to the parent directory.

        Returns:
            List[Tuple[str, int, str]]: A list of tuples representing the directory structure.
        """
        structure = []

        for key, value in node.items():
            if key == '__keys__':
                continue  # Skip metadata
            item_name = key.rstrip('/')  # Remove trailing '/' if any
            current_path = os.path.join(parent_path, item_name)
            is_dir = key.endswith('/')

            # Add the item to the structure
            structure.append((current_path, level, item_name))

            if is_dir:
                # Recurse into the directory
                structure.extend(JSONStyle._traverse_json(value, level + 1, current_path))

        return structure


