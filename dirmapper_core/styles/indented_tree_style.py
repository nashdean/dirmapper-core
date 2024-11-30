from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle
from dirmapper_core.utils import utils

class IndentedTreeStyle(BaseStyle):
    """
    IndentedTreeStyle class for generating a directory structure in an indented tree format.
    """
    @staticmethod
    def write_structure(structure: List[Tuple[str, int, str]] | dict, **kwargs) -> str:
        """
        Write the directory structure in an indented tree format.

        Args:
            structure (list | dict): The directory structure to write. Each tuple contains (item_path, level, item).
            **kwargs: Additional keyword arguments.

        Returns:
            str: The directory structure in an indented tree format.

        Example:
            Parameters:
                structure = [
                    ('/path/to/root/dir', 0, '/path/to/root/dir'),
                    ('file1.txt', 1, 'file1.txt'),
                    ('file2.txt', 1, 'file2.txt'),
                    ('sub_dir1', 1, 'sub_dir1'),
                    ('sub_dir1/sub_dir2', 2, 'sub_dir2'),
                    ('sub_dir1/sub_dir2/file3.txt', 3, 'file3.txt'),
                    ('sub_dir1/sub_dir2/file4.txt', 3, 'file4.txt'),
                    ('sub_dir3', 1, 'sub_dir3'),
                    ('sub_dir3/file5.txt', 2, 'file5.txt')
                ]
            Result:
                /path/to/root/dir
                ├── file1.txt
                ├── file2.txt
                └── sub_dir1/
                    └── sub_dir2/
                        ├── file3.txt
                        └── file4.txt
                └── sub_dir3/
                    └── file5.txt
        """
        result = []
        if isinstance(structure, list):
            n = len(structure)
            for i, (item_path, level, item) in enumerate(structure):
                if level == 0:
                    # Root directory
                    result.append(f"{item_path}")
                    continue

                # Determine if this is the last item at its level
                is_last = utils.is_last_item(structure, i, level)

                # Build the indentation
                indent = '    ' * (level - 1)
                
                # Append '/' to directories
                if os.path.isdir(os.path.join(kwargs.get('root_dir', ''), item_path)):
                    item += '/'
                
                # Determine if the item is a directory
                is_dir = utils.is_directory(item)

                # Determine the connector
                connector = '└── ' if is_last or is_dir else '├── '

                # Append the line
                result.append(f"{indent}{connector}{item}")

        return '\n'.join(result)
    
    @staticmethod
    def parse_from_style(tree_str: str, root_dir: str = "") -> List[Tuple[str, int, str]]:
        """
        Parse a tree-style string back into a list of tuples representing the directory structure.

        Args:
            tree_str (str): The tree-style string.
            root_dir (str): The root directory path to prepend to all paths.

        Returns:
            List[Tuple[str, int, str]]: A list of tuples representing the directory structure.
        """
        import re

        lines = tree_str.strip().splitlines()
        structure = []
        parent_paths = []
        indent_unit = 4  # Number of spaces per indentation level

        for idx, line in enumerate(lines):
            # Handle the root directory (level 0)
            if idx == 0:
                root_name = line.strip()
                structure.append((root_name, 0, root_name))
                parent_paths = [root_name]
                continue

            # Determine the indentation level
            indent_match = re.match(r'^(\s*)([├└]── )?(.*)', line)
            if not indent_match:
                continue  # Skip lines that don't match the expected pattern

            indent_str, connector, item_name = indent_match.groups()
            indent_length = len(indent_str)
            level = (indent_length // indent_unit) + 1  # +1 to account for root level

            # Remove any trailing '/' from item_name
            item_name = item_name.rstrip('/')

            # Update parent_paths based on level
            if level > len(parent_paths):
                # Going deeper, add the last item to parent_paths
                pass  # parent_paths already contains the correct path
            elif level == len(parent_paths):
                # Same level, replace the last item
                parent_paths = parent_paths[:-1]
            else:
                # Moving up, truncate parent_paths
                parent_paths = parent_paths[:level - 1]

            # Build current path
            if len(parent_paths) > 0:
                current_path = os.path.join(parent_paths[-1], item_name)
            else:
                current_path = item_name  # Should not happen, but added for safety

            # Add the current item to the structure
            structure.append((current_path, level, item_name))

            # Check if the item is a directory (next line is indented more)
            is_dir = False
            if idx + 1 < len(lines):
                next_line = lines[idx + 1]
                next_indent_match = re.match(r'^(\s*)([├└]── )?(.*)', next_line)
                if next_indent_match:
                    next_indent_str = next_indent_match.group(1)
                    next_indent_length = len(next_indent_str)
                    next_level = (next_indent_length // indent_unit) + 1
                    if next_level > level:
                        is_dir = True
            else:
                is_dir = False  # Last line

            if is_dir:
                # Append current path to parent_paths
                parent_paths.append(current_path)

        return structure

