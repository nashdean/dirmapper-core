from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle

class IndentationStyle(BaseStyle):
    """
    IndentationStyle class for generating a directory structure in an indented format.
    """
    #TODO: Update this method to work with the template summarizer; see tree_style for details
    def write_structure(self, structure: List[Tuple[str, int, str]], **kwargs) -> str:
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
               └── dir1/
                     ├── file1.txt
                     ├── file2.txt
                     └── subdir1/
                          └── file3.txt
        """
        result = []
        for i, (item_path, level, item) in enumerate(structure):
            indent = '    ' * level
            is_last = (i == len(structure) - 1 or structure[i + 1][1] < level)
            connector = '└── ' if is_last else '├── '

            if os.path.isdir(item_path):
                result.append(f"{indent}{connector}{item}/")
            else:
                result.append(f"{indent}{connector}{item}")
        
        return '\n'.join(result)
