import re
from typing import List, Tuple
import os
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.styles.base_style import BaseStyle

class IndentationStyle(BaseStyle):
    """
    IndentationStyle class for generating a directory structure in an indented format.
    """
    #TODO: Update this method to work with the template summarizer; see tree_style for details
    @staticmethod
    def write_structure(structure: DirectoryStructure, **kwargs) -> str:
        """
        Write the directory structure in an indented format. Similar to the tree format,
        but without trunk/straight pipe characters.

        Args:
            structure (DirectoryStructure): The directory structure to write.
                `structure` is a DirectoryStructure object containing DirectoryItem objects.
            **kwargs:
                - root_dir (str): The root directory path.

        Returns:
            str: The directory structure in an indented format.
        
        Example:
            Parameters:
                structure = DirectoryStructure()
                structure.add_item(DirectoryItem('/path/to/root/dir', 0, 'dir'))
                structure.add_item(DirectoryItem('file1.txt', 1, 'file1.txt'))
                structure.add_item(DirectoryItem('file2.txt', 1, 'file2.txt'))
                structure.add_item(DirectoryItem('subdir', 1, 'subdir'))
                structure.add_item(DirectoryItem('subdir/file3.txt', 2, 'file3.txt'))

            Result:
                /path/to/root/dir
                file1.txt
                file2.txt
                subdir
                    file3.txt
        """
        root_dir = kwargs.get('root_dir', '')
        items = structure.to_list()
        result = []

        for item in items:
            if item.level == 0:
                # Root directory
                result.append(f"{item.path}")
                continue
            indent = '    ' * (item.level - 1)
            result.append(f"{indent}{item.name}")

        return '\n'.join(result)
    
    @staticmethod
    def parse_from_style(indent_str: str) -> DirectoryStructure:
        """
        Parse an indented structure string back into a DirectoryStructure object.

        Args:
            indent_str (str): The indented structure string.

        Returns:
            DirectoryStructure: A DirectoryStructure object representing the directory structure.
        
        Example:
            Given an indented string:
                /Users/nashdean/dirmap/fake_proj
                .gitignore
                pyproject.toml
                README.md
                src
                    tiny_project
                        __init__.py
                        main.py
                tests
                    test_main.py

            The returned DirectoryStructure would contain DirectoryItems:
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj', level=0, name='/Users/nashdean/dirmap/fake_proj')
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj/.gitignore', level=1, name='.gitignore')
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj/pyproject.toml', level=1, name='pyproject.toml')
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj/README.md', level=1, name='README.md')
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj/src', level=1, name='src')
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj/src/tiny_project', level=2, name='tiny_project')
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj/src/tiny_project/__init__.py', level=3, name='__init__.py')
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj/src/tiny_project/main.py', level=3, name='main.py')
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj/tests', level=1, name='tests')
                DirectoryItem(path='/Users/nashdean/dirmap/fake_proj/tests/test_main.py', level=2, name='test_main.py')
        """
        lines = indent_str.strip().splitlines()
        structure = DirectoryStructure()
        parent_paths = []
        indent_unit = 4  # Number of spaces per indentation level

        if not lines:
            return structure

        # The first line is the absolute root directory
        root_name = lines[0].strip()
        # Add the root directory item
        root_item = DirectoryItem(path=root_name, level=0, name=root_name)
        structure.add_item(root_item)
        parent_paths = [root_name]  # parent_paths now starts with the absolute root directory

        for idx, line in enumerate(lines[1:], start=1):
            stripped_line = line.lstrip()
            indent_length = len(line) - len(stripped_line)
            level = (indent_length // indent_unit) + 1  # +1 to account for root level

            item_name = stripped_line.rstrip('/')

            # Update parent_paths based on the current level
            parent_paths = parent_paths[:level]
            parent_paths.append(item_name)

            # Build the absolute path by joining the root directory and the relative components
            # Since parent_paths[0] is already the absolute root, we can just join all of them
            absolute_path = os.path.join(*parent_paths)

            # Create a DirectoryItem with the absolute path
            item = DirectoryItem(path=absolute_path, level=level, name=item_name)
            structure.add_item(item)

        return structure