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
    def write_structure(self, structure: List[Tuple[str, int, str]], **kwargs) -> dict:
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
            
        def build_json_structure(structure, level: int) -> Tuple[dict, int]:
            """
            Builds the modified JSON-like structure with real metadata.
            """
            result = {}
            i = 0
            while i < len(structure):
                item_path, item_level, item_name = structure[i]
                is_dir = os.path.isdir(item_path)
                metadata = get_metadata(item_path, is_dir)

                if is_dir:
                    folder_key = f"{item_name}/"
                    sub_structure, sub_items = build_json_structure(structure[i + 1:], level + 1)
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
                    i += sub_items
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
                i += 1

            return result, i

        # Start building the structure at level 0
        root_path, _, root_name = structure[0]
        _, root_level, _ = structure[0]
        json_structure, _ = build_json_structure(structure[1:], root_level + 1)

        # Include metadata for the root directory and attach its contents
        return {
            root_path: {
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