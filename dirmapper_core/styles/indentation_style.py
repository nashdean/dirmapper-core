import re
from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle

class IndentationStyle(BaseStyle):
    """
    IndentationStyle class for generating a directory structure in an indented format.
    """
    #TODO: Update this method to work with the template summarizer; see tree_style for details
    @staticmethod
    def write_structure(structure: List[Tuple[str, int, str]], **kwargs) -> str:
        """
        Write the directory structure in an indented format. Similar to the tree format, but without the trunk/straight pipe characters.

        Args:
            structure (list): The directory structure to write. The structure should be a list of tuples. Each tuple should contain the path, level, and item name.

        Returns:
            str: The directory structure in an indented format.
        
        Example:
            Parameters:
                structure = [
                    ('dir1/', 0, 'dir1'),
                    ('dir1/file1.txt', 1, 'file1.txt'),
                    ('dir1/file2.txt', 1, 'file2.txt'),
                    ('dir1/subdir1/', 1, 'subdir1'),
                    ('dir1/subdir1/file3.txt', 2, 'file3.txt')
                ]
            Result:
                path/to/root
                dir1/
                    file1.txt
                    file2.txt
                    subdir1/
                        file3.txt
        """
        root_dir = kwargs.get('root_dir', '')
        result = []
        if isinstance(structure, list):
            for item_path, level, item in structure:
                if level == 0:
                    # Root directory
                    result.append(f"{item_path}")
                    continue
                indent = '    ' * (level - 1)
                result.append(f"{indent}{item}")
            return '\n'.join(result)
    
    @staticmethod
    def parse_from_style(indent_str: str, root_dir: str = "") -> List[Tuple[str, int, str]]:
        """
        Parse an indented structure string back into a list of tuples representing
        the directory structure.

        Args:
            indent_str (str): The indented structure string.
            root_dir (str): The root directory path to prepend to all paths.

        Returns:
            List[Tuple[str, int, str]]: A list of tuples representing the directory structure.
        """
        lines = indent_str.strip().splitlines()
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
            stripped_line = line.lstrip()
            indent_length = len(line) - len(stripped_line)
            level = (indent_length // indent_unit) + 1  # +1 to account for root level

            item_name = stripped_line.rstrip('/')

            # Update parent_paths to reflect the current level
            parent_paths = parent_paths[:level]
            parent_paths.append(item_name)

            # Build current path relative to the root
            if len(parent_paths) > 1:
                # Exclude the root_name when constructing the relative path
                current_path = os.path.join(*parent_paths[1:])
            else:
                current_path = item_name  # For items at level 1

            # Add the current item to the structure
            structure.append((current_path, level, item_name))

        return structure
