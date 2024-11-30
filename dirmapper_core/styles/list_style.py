from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle

class ListStyle(BaseStyle):
    """
    ListStyle class for generating a directory structure in a list format.
    """
    #TODO: Update this method to work with the template summarizer; see tree_style for details
    @staticmethod
    def write_structure(structure: List[Tuple[str, int, str]], **kwargs) -> str:
        """
        Write the directory structure in a list format.
        
        Args:
            structure (list): The directory structure to write. The structure should be a list of tuples. Each tuple should contain the path, level, and item name.
            
        Returns:
            str: The directory structure in a list format.
        
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
                - dir1/
                    - file1.txt
                    - file2.txt
                    - subdir1/
                        - file3.txt
        """
        root_dir = kwargs.get('root_dir', '')  # Get root_dir from kwargs if needed
        result = []
        if isinstance(structure, list):
            for item_path, level, item in structure:
                if level == 0:
                    # Root directory
                    result.append(f"{item_path}")
                    continue
                indent = '    ' * (level - 1)  # Adjust indentation
                result.append(f"{indent}- {item}")
            return '\n'.join(result)
        
    @staticmethod
    def parse_from_style(list_str: str, root_dir: str = "") -> List[Tuple[str, int, str]]:
        """
        Parse a list structure string back into a list of tuples representing
        the directory structure.

        Args:
            list_str (str): The list structure string.
            root_dir (str): The root directory path to prepend to all paths.

        Returns:
            List[Tuple[str, int, str]]: A list of tuples representing the directory structure.
        """
        lines = list_str.splitlines()
        structure = []
        parent_paths = []  # Stack to manage parent paths based on levels

        for line in lines:
            # Determine the level based on indentation
            stripped_line = line.lstrip()
            indent_length = len(line) - len(stripped_line)
            level = indent_length // 4  # Each level of indentation is 4 spaces

            # Remove the '- ' prefix while keeping trailing '/' for directories
            item_name = stripped_line.lstrip('- ')
            is_folder = item_name.endswith('/')

            # Build the path
            if level == 0:
                # Root item
                current_path = os.path.join(root_dir, item_name.rstrip('/'))
                parent_paths = [current_path]
            else:
                # Update parent_paths stack
                if level < len(parent_paths):
                    parent_paths = parent_paths[:level]
                current_path = os.path.join(parent_paths[-1], item_name.rstrip('/'))
                if is_folder:
                    parent_paths.append(current_path)

            # Add the item to the structure, keeping trailing '/' for directories
            structure.append((current_path + '/' if is_folder else current_path, level, item_name))

        return structure

