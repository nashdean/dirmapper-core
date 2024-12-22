import re
from typing import List, Optional, Tuple
import os
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.styles.base_style import BaseStyle
import dirmapper_core.utils.utils as utils

class TreeStyle(BaseStyle):
    """
    TreeStyle class for generating a directory structure in a tree format.
    """
    @staticmethod
    def write_structure(structure: DirectoryStructure, **kwargs) -> str:
        """
        Write the directory structure in a tree format.

        Args:
            structure (DirectoryStructure): The directory structure to write. The structure should be an instance of DirectoryStructure containing DirectoryItem instances.

        Returns:
            str: The directory structure in a tree format.

        Example:
            Parameters:
                structure = DirectoryStructure()
                structure.add_item(DirectoryItem('/path/to/root/dir', 0, '/path/to/root/dir'))
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
        levels_has_next = []
        for i, item in enumerate(structure.to_list()):
            if item.level == 0:
                result.append(f"{item.path}")
                levels_has_next = []
                continue

            is_last = utils.is_last_item(structure.to_list(), i, item.level)
            if len(levels_has_next) < item.level:
                levels_has_next.extend([True] * (item.level - len(levels_has_next)))
            levels_has_next[item.level - 1] = not is_last

            indent = ''
            for lvl in range(item.level - 1):
                if levels_has_next[lvl]:
                    indent += '│   '
                else:
                    indent += '    '
            connector = '└── ' if is_last else '├── '

            full_item_path = os.path.join(root_dir, item.path)
            if os.path.isdir(full_item_path):
                result.append(f"{indent}{connector}{item.name}/")
            else:
                result.append(f"{indent}{connector}{item.name}")

        return '\n'.join(result)
    
    @staticmethod
    def parse_from_style(tree_str: str) -> DirectoryStructure:
        """
        Parse a tree structure string back into a DirectoryStructure.

        Args:
            tree_str (str): The tree structure string.

        Returns:
            DirectoryStructure: The parsed directory structure.
        """
        lines = tree_str.strip().splitlines()
        structure = DirectoryStructure()
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
                structure.add_item(DirectoryItem(current_path, level, item_name))
                parent_paths = [current_path]
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
            else:
                current_path = name  # Should not happen, but added for safety

            structure.add_item(DirectoryItem(current_path, level, name))

            if is_folder:
                parent_paths.append(current_path)

        return structure

    @staticmethod
    def write_structure_lines(structure: DirectoryStructure) -> List[Tuple[str, DirectoryItem]]:
        """
        Similar to write_structure, but returns a list of (line, DirectoryItem) pairs.
        We'll replicate the logic from write_structure exactly, but store item references.
        """
        items = structure.to_list()
        lines_and_items = []
        levels_has_next = []

        for i, item in enumerate(items):
            if item.level == 0:
                line = f"{item.path}"
                lines_and_items.append((line, item))
                levels_has_next = []
                continue

            is_last = utils.is_last_item(items, i, item.level)
            if len(levels_has_next) < item.level:
                levels_has_next.extend([True] * (item.level - len(levels_has_next)))
            levels_has_next[item.level - 1] = not is_last

            indent = ''
            for lvl in range(item.level - 1):
                if levels_has_next[lvl]:
                    indent += '│   '
                else:
                    indent += '    '
            connector = '└── ' if is_last else '├── '

            # Decide if directory or file
            # We'll check item.metadata['type'] == 'directory' or fallback to name with trailing slash
            is_dir = ('type' in item.metadata and item.metadata['type'] == 'directory') or os.path.isdir(item.path)
            if is_dir:
                line = f"{indent}{connector}{item.name}/"
            else:
                line = f"{indent}{connector}{item.name}"
            lines_and_items.append((line, item))

        return lines_and_items

    @staticmethod
    def write_structure_with_short_summaries(structure: DirectoryStructure) -> str:
        """
        Write the directory structure in a tree format with aligned short summaries as comments.
        """
        lines_and_items = TreeStyle.write_structure_lines(structure)
        if not lines_and_items:
            return ""

        # Find max line length
        max_line_length = max(len(line) for line, _ in lines_and_items)

        result_lines = []
        for line, item in lines_and_items:
            short_summary = item.metadata.get('short_summary') if item.metadata else None
            if not short_summary:
                short_summary = "No summary" if item.metadata and item.metadata.get('type') == 'file' else ""

            spacing = " " * (max_line_length - len(line) + 2)  # 2 spaces before '#'
            result_lines.append(f"{line}{spacing}# {short_summary}")

        return "\n".join(result_lines)