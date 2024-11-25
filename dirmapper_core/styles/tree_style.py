from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle

class TreeStyle(BaseStyle):
    """
    TreeStyle class for generating a directory structure in a tree format.
    """
    def write_structure(self, structure: List[Tuple[str, int, str]] | dict, **kwargs) -> str:
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
                is_last = self._is_last_item(structure, i, level)

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
            self._write_from_dict(structure, '', True, lines)

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
    
    def _write_from_dict(self, structure: dict | list, prefix: str, is_last: bool, lines: list, level: int=0) -> None:
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
                indent = self._get_indent(level)
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
                    self._write_from_dict(child_structure, prefix + key + '/', is_last_item, lines, level + 1)
                elif isinstance(value, list):
                    self._write_from_list(value, prefix + key + '/', is_last_item, lines, level + 1)
        elif isinstance(structure, list):
            self._write_from_list(structure, prefix, is_last, lines, level)
    
    def _write_from_list(self, structure, prefix, is_last, lines, level):
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
            self._write_from_dict(item, prefix, is_last_item, lines, level)
    
    def _get_indent(self, level):
        """
        Get the indentation string for the specified level. Helper method for _write_from_dict.

        Args:
            level (int): The level of depth in the directory structure.
        
        Returns:
            str: The indentation string.
        """
        return '│   ' * level
    
    def _is_last_item(self, structure, index, current_level):
        # Check if there is any next item at the same level
        for next_index in range(index + 1, len(structure)):
            next_level = structure[next_index][1]
            if next_level == current_level:
                return False  # There is another item at the same level
            elif next_level < current_level:
                break
        return True  # No more items at the same level