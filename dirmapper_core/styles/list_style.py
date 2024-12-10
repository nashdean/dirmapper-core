from typing import List, Tuple
import os
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.styles.base_style import BaseStyle

class ListStyle(BaseStyle):
    """
    ListStyle class for generating a directory structure in a list format.
    """
    @staticmethod
    def write_structure(structure: DirectoryStructure, **kwargs) -> str:
        """
        Write the directory structure in a list format.
        
        Args:
            structure (DirectoryStructure): The directory structure to write. The structure should be an instance of DirectoryStructure containing DirectoryItem instances.
            
        Returns:
            str: The directory structure in a list format.
        
        Example:
            Parameters:
                structure = DirectoryStructure()
                structure.add_item(DirectoryItem('/path/to/root/dir', 0, 'root'))
                structure.add_item(DirectoryItem('file1.txt', 1, 'file1.txt'))
                structure.add_item(DirectoryItem('file2.txt', 1, 'file2.txt'))
                structure.add_item(DirectoryItem('sub_dir1', 1, 'sub_dir1'))
                structure.add_item(DirectoryItem('sub_dir1/sub_dir2', 2, 'sub_dir2'))
                structure.add_item(DirectoryItem('sub_dir1/sub_dir2/file3.txt', 3, 'file3.txt'))
                structure.add_item(DirectoryItem('sub_dir1/sub_dir2/file4.txt', 3, 'file4.txt'))
                structure.add_item(DirectoryItem('sub_dir3', 1, 'sub_dir3'))
                structure.add_item(DirectoryItem('sub_dir3/file5.txt', 2, 'file5.txt'))
            Result:
                /path/to/root/dir
                - file1.txt
                - file2.txt
                - sub_dir1/
                    - sub_dir2/
                        - file3.txt
                        - file4.txt
                - sub_dir3/
                    - file5.txt
        """
        root_dir = kwargs.get('root_dir', '')  # Get root_dir from kwargs if needed
        result = []
        for item in structure.to_list():
            if item.level == 0:
                # Root directory
                result.append(f"{item.path}")
                continue
            indent = '    ' * (item.level - 1)  # Adjust indentation
            full_item_path = os.path.join(root_dir, item.path)
            if os.path.isdir(full_item_path):
                result.append(f"{indent}- {item.name}/")
            else:
                result.append(f"{indent}- {item.name}")
        return '\n'.join(result)
        
    @staticmethod
    def parse_from_style(list_str: str) -> List[Tuple[str, int, str]]:
        """
        Parse a list structure string back into a DirectoryStructure object.

        Args:
            list_str (str): The list structure string.

        Returns:
            DirectoryStructure: The parsed directory structure.
        """
        lines = list_str.splitlines()
        structure = DirectoryStructure()
        parent_paths = []
        root_processed = False

        # Preprocess lines to get levels
        levels = []
        for line in lines:
            stripped_line = line.lstrip()
            indent_length = len(line) - len(stripped_line)
            level = indent_length // 4  # Each level of indentation is 4 spaces
            levels.append(level)

        for i, line in enumerate(lines):
            # Determine the level based on indentation
            stripped_line = line.lstrip()
            indent_length = len(line) - len(stripped_line)
            level = indent_length // 4  # Each level of indentation is 4 spaces

            # Remove the '- ' prefix and trailing '/' for directories
            item_name = stripped_line.lstrip('- ').rstrip('/')
            # Assume items with child items are directories
            if i + 1 < len(lines) and levels[i + 1] > level:
                is_folder = True
            else:
                is_folder = False

            if not root_processed:
                # Process the first line as the root item
                current_path = os.path.join(root_dir, item_name.rstrip('/'))
                parent_paths = [current_path]
                root_dir = current_path  # Set root_dir to current_path
                structure.add_item(DirectoryItem(current_path, 0, item_name))
                root_processed = True
                continue
            else:
                # For subsequent lines
                level += 1  # Adjust level to account for root
                # Update parent_paths stack
                if level <= len(parent_paths):
                    parent_paths = parent_paths[:level - 1]
                if parent_paths:
                    current_path = os.path.join(parent_paths[-1], item_name.rstrip('/'))
                else:
                    current_path = os.path.join(root_dir, item_name.rstrip('/'))

                if is_folder:
                    parent_paths.append(current_path)

                # Compute the relative path to the root directory
                relative_current_path = os.path.relpath(current_path, start=root_dir) # Not Used, Returning Full Path instead

                # Add the item to the structure
                structure.add_item(DirectoryItem(current_path, level, item_name))

        return structure
