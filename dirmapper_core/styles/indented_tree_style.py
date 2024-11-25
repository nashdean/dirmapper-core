from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle

class IndentedTreeStyle(BaseStyle):
    """
    IndentedTreeStyle class for generating a directory structure in an indented tree format.
    """
    def write_structure(self, structure: List[Tuple[str, int, str]] | dict, **kwargs) -> str:
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
                    ('dir1/', 0, 'dir1'),
                    ('dir1/file1.txt', 1, 'file1.txt'),
                    ('dir1/file2.txt', 1, 'file2.txt'),
                    ('dir1/subdir1/', 1, 'subdir1'),
                    ('dir1/subdir1/file3.txt', 2, 'file3.txt')
                ]
            Result:
                path/to/root
                └── dir1/
                    ├── file1.txt
                    ├── file2.txt
                    └── subdir1/
                        └── file3.txt
        """
        root_dir = kwargs.get('root_dir', '')
        result = []
        if isinstance(structure, list):
            for i, (item_path, level, item) in enumerate(structure):
                if level == 0:
                    # Root directory
                    result.append(f"{item_path}")
                    continue  # Skip to next item
                indent = '    ' * level  # Indent with spaces
                # Determine if this is the last item at the current level
                is_last = self._is_last_item(structure, i, level)
                connector = '└── ' if is_last else '├── '

                full_item_path = os.path.join(root_dir, item_path)
                if os.path.isdir(full_item_path):
                    result.append(f"{indent}{connector}{item}/")
                else:
                    result.append(f"{indent}{connector}{item}")

            return '\n'.join(result)
        elif isinstance(structure, dict):
            # Handle dict structures if necessary
            pass

    def _is_last_item(self, structure, index, current_level):
        # Check if the next item is at a higher level
        next_index = index + 1
        if next_index >= len(structure):
            return True
        next_level = structure[next_index][1]
        return next_level <= current_level
