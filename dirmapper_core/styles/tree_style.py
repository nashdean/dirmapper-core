import re
from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle
import dirmapper_core.utils.utils as utils

class TreeStyle(BaseStyle):
    """
    TreeStyle class for generating a directory structure in a tree format.
    """
    @staticmethod
    def write_structure(structure: List[Tuple[str, int, str]] | dict, **kwargs) -> str:
        """
        Write the directory structure in a tree format.

        Args:
            structure (list | dict): The directory structure to write. The structure can be a list of tuples or a dictionary. Each tuple should contain the path, level, and item name. The dictionary should be a structured representation of the directory structure.

        Returns:
            str: The directory structure in a tree format.

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
                ├── sub_dir1/
                │   └── sub_dir2/
                │       ├── file3.txt
                │       └── file4.txt
                └── sub_dir3/
                    └── file5.txt
        """
        root_dir = kwargs.get('root_dir', '')
        result = []
        if isinstance(structure, list):
            levels_has_next = []
            for i, (item_path, level, item) in enumerate(structure):
                if level == 0:
                    # Root directory
                    result.append(f"{item_path}")
                    levels_has_next = []  # Reset levels_has_next for root
                    continue  # Skip to next item

                # Determine if this is the last item at its level
                is_last = TreeStyle._is_last_item(structure, i, level)

                # Update levels_has_next
                if len(levels_has_next) < level:
                    levels_has_next.extend([True] * (level - len(levels_has_next)))
                levels_has_next[level - 1] = not is_last

                # Build the indentation
                indent = ''
                for lvl in range(level - 1):
                    if levels_has_next[lvl]:
                        indent += '│   '
                    else:
                        indent += '    '
                connector = '└── ' if is_last else '├── '

                full_item_path = os.path.join(root_dir, item_path)
                if os.path.isdir(full_item_path):
                    result.append(f"{indent}{connector}{item}/")
                else:
                    result.append(f"{indent}{connector}{item}")

            return '\n'.join(result)
    
    def parse_from_style(tree_str: str, root_dir: str = "") -> List[Tuple[str, int, str]]:
        """
        Parse a tree structure string back into a list of tuples representing
        the directory structure.

        Args:
            tree_str (str): The tree structure string.
            root_dir (str): The root directory path to prepend to all paths.

        Returns:
            List[Tuple[str, int, str]]: A list of tuples representing the directory structure.
        """
        lines = tree_str.strip().splitlines()
        structure = []
        parent_paths = []  # Stack to manage parent paths based on levels

        root_dir_included = False

        for line_num, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                continue

            # Detect root line
            if not root_dir_included and not re.match(r'^\s*[│├└]', line):
                # This is the root directory
                item_name = line.strip()
                level = 0
                current_path = item_name
                parent_paths = [""]  # Include an empty string for the root directory
                structure.append((current_path, level, item_name))
                root_dir_included = True
                continue

            # Clean up the line
            # Replace '│   ' with '\t'
            line_clean = line.replace('│   ', '\t')
            # Replace '    ' (4 spaces) with '\t'
            line_clean = line_clean.replace('    ', '\t')
            # Replace any remaining '│' with '\t' (in case of single '│' characters)
            line_clean = line_clean.replace('│', '\t')

            # Match indent and name
            indent_match = re.match(r'^(?P<indent>\t*)([├└][─]{2} )?(?P<name>.+)', line_clean)
            if not indent_match:
                continue  # Skip lines that don't match the pattern

            indent_str = indent_match.group('indent')
            name = indent_match.group('name').rstrip('/').strip()
            is_folder = line.strip().endswith('/')

            # Calculate level
            level = len(indent_str) + 1  # +1 because root is level 0

            # Update parent_paths
            if level <= len(parent_paths):
                parent_paths = parent_paths[:level]
            else:
                # Extend parent_paths if we're deeper than before
                pass  # This case will naturally be handled when we append to parent_paths

            if parent_paths:
                parent = parent_paths[-1]
                current_path = os.path.join(parent, name)
            # else:
            #     # Should not reach here because root directory should be included
            #     current_path = os.path.join(root_dir, name)

            if is_folder:
                parent_paths.append(current_path)

            structure.append((current_path, level, name))

        return structure
    
    def _get_indent(level):
        """
        Get the indentation string for the specified level. Helper method for _write_from_dict.

        Args:
            level (int): The level of depth in the directory structure.
        
        Returns:
            str: The indentation string.
        """
        return '│   ' * level