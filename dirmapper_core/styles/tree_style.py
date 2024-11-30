import re
from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle

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
                    ('dir1/', 0, 'dir1'),
                    ('dir1/file1.txt', 1, 'file1.txt'),
                    ('dir1/file2.txt', 1, 'file2.txt'),
                    ('dir1/subdir1/', 1, 'subdir1'),
                    ('dir1/subdir1/file3.txt', 2, 'file3.txt')
                ]
            Result:
                path/to/root
                dir1/
                ├── file1.txt
                ├── file2.txt
                └── subdir1/
                    └── file3.txt
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
        elif isinstance(structure, dict):
            lines = []
            TreeStyle._write_from_dict(structure, '', True, lines)

            # Calculate the maximum length of lines before comments
            max_length = max(len(line[0]) for line in lines) if lines else 0

            # Format lines with aligned comments
            formatted_lines = []
            for line_content, comment in lines:
                if comment:
                    formatted_lines.append(f"{line_content.ljust(max_length)}  # {comment}")
                else:
                    formatted_lines.append(line_content)
            return '\n'.join(formatted_lines)
    
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

    @staticmethod
    def _write_from_dict(structure: dict | list, prefix: str, is_last: bool, lines: list, level: int=0) -> None:
        """
        Recursively write the directory structure from a dictionary by modifying the lines list in place.
        
        Args:
            structure (dict): The directory structure to write.
            prefix (str): The prefix to add to the path.
            is_last (bool): Flag indicating whether the current item is the last in the list.
            lines (list): The list of lines to write the structure to.
            level (int): The current level of depth in the directory structure.

        Returns:

        Example:
            Parameters:
                structure = {
                    "dir1": {
                        "file1.txt": {},
                        "file2.txt": {},
                        "subdir1": {
                            "file3.txt": {}
                        }
                    }
                }
                prefix = ''
                is_last = True
                lines = []
                level = 0
            Result:
                lines = [
                    ('dir1/', ''),
                    ('├── file1.txt', ''),
                    ('├── file2.txt', ''),
                    ('└── subdir1/', ''),
                    ('    └── file3.txt', '')
                ]
            """
        if isinstance(structure, dict):
            items = list(structure.items())
            for idx, (key, value) in enumerate(items):
                is_last_item = idx == len(items) - 1
                connector = '└── ' if is_last_item else '├── '
                indent = TreeStyle._get_indent(level)
                line = f"{indent}{connector}{key}"
                summary = ''
                if isinstance(value, dict) and 'summary' in value:
                    summary = value['summary']
                # if isinstance(value, dict) or isinstance(value, list):
                #     if not summary:
                #         line += '/'
                lines.append((line, summary))
                if isinstance(value, dict):
                    # Exclude the 'summary' key when recursing
                    child_structure = {k: v for k, v in value.items() if k != 'summary'}
                    TreeStyle._write_from_dict(child_structure, prefix + key + '/', is_last_item, lines, level + 1)
                elif isinstance(value, list):
                    TreeStyle._write_from_list(value, prefix + key + '/', is_last_item, lines, level + 1)
        elif isinstance(structure, list):
            TreeStyle._write_from_list(structure, prefix, is_last, lines, level)
    
    def _write_from_list(structure, prefix, is_last, lines, level):
        """
        Recursively write the directory structure from a list by modifying the lines list in place.
        Helper method for _write_from_dict.
        
        Args:
            structure (list): The directory structure to write.
            prefix (str): The prefix to add to the path.
            is_last (bool): Flag indicating whether the current item is the last in the list.
            lines (list): The list of lines to write the structure to.
            level (int): The current level of depth in the directory structure.
            
        Returns:
        
        Example:
            Parameters:
                structure = [
                    {
                        "dir1": {
                            "file1.txt": {},
                            "file2.txt": {},
                            "subdir1": {
                                "file3.txt": {}
                            }
                        }
                    },
                    {
                        "dir2": {
                            "file4.txt": {},
                            "file5.txt": {},
                            "subdir2": {
                                "file6.txt": {}
                            }
                        }
                    }
                ]
                prefix = ''
                is_last = True
                lines = []
                level = 0
            Result:
                lines = [
                    ('dir1/', ''),
                    ('├── file1.txt', ''),
                    ('├── file2.txt', ''),
                    ('└── subdir1/', ''),
                    ('    └── file3.txt', ''),
                    ('dir2/', ''),
                    ('├── file4.txt', ''),
                    ('├── file5.txt', ''),
                    ('└── subdir2/', ''),
                    ('    └── file6.txt', '')
                ]
            """
        for idx, item in enumerate(structure):
            is_last_item = idx == len(structure) - 1
            TreeStyle._write_from_dict(item, prefix, is_last_item, lines, level)
    
    def _get_indent(level):
        """
        Get the indentation string for the specified level. Helper method for _write_from_dict.

        Args:
            level (int): The level of depth in the directory structure.
        
        Returns:
            str: The indentation string.
        """
        return '│   ' * level
    
    def _is_last_item(structure, index, current_level):
        # Check if there is any next item at the same level
        for next_index in range(index + 1, len(structure)):
            next_level = structure[next_index][1]
            if next_level == current_level:
                return False  # There is another item at the same level
            elif next_level < current_level:
                break
        return True  # No more items at the same level