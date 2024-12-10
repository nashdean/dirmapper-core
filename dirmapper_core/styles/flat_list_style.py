import os
from typing import List, Tuple
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.styles.base_style import BaseStyle

class FlatListStyle(BaseStyle):
    """
    FlatListStyle is a concrete class that inherits from the BaseStyle class. It provides an implementation for the write_structure method that converts a directory structure into a flat list representation.
    """
    def write_structure(structure: DirectoryStructure, **kwargs) -> str:
        """
        Takes a list of tuples representing the directory structure and returns a flat list representation of the structure.

        Args:
            - structure (List[Tuple[str, int, str]]): A list of tuples where each tuple contains the path to the file or directory, the level of indentation, and the name of the file or directory.

        Returns:
            - str: A flat list representation of the directory structure.

        Example:
            Parameters:
                structure = DirectoryStructure()
                structure.add_item(DirectoryItem('/absolute/path/to/dir', 0, '/absolute/path/to/dir'))
                structure.add_item(DirectoryItem('/absolute/path/to/dir/file1.txt', 1, 'file1.txt'))
                structure.add_item(DirectoryItem('/absolute/path/to/dir/file2.txt', 1, 'file2.txt'))
                structure.add_item(DirectoryItem('/absolute/path/to/dir/subdir', 1, 'subdir'))
                structure.add_item(DirectoryItem('/absolute/path/to/dir/subdir/file3.txt', 2, 'file3.txt'))


            Result:
                /path/to/dir
                /path/to/dir/file1.txt
                /path/to/dir/file2.txt
                /path/to/dir/subdir
                /path/to/dir/subdir/file3.txt
        """
        result = [item_path for item_path, _, _ in structure]
        return '\n'.join(result)

    @staticmethod
    def parse_from_style(flat_list_str: str) -> DirectoryStructure:
        """
        Parse a flat list of paths back into a list of tuples representing the
        directory structure.

        Args:
            flat_list_str (str): The flat list of paths, one per line.

        Returns:
            List[Tuple[str, int, str]]: A list of tuples representing the
                                        directory structure.
        """
        lines = flat_list_str.strip().splitlines()
        structure = DirectoryStructure()

        if not lines:
            return structure

        # The first line is the absolute root directory
        root_path = lines[0].strip()
        # Add the root directory item (level 0)
        root_item = DirectoryItem(path=root_path, level=0, name=root_path)
        structure.add_item(root_item)

        for line in lines[1:]:
            path = line.strip()
            # Calculate the relative path to the root directory
            relative_path = os.path.relpath(path, start=root_path)
            # Split the relative path into components
            path_components = relative_path.split(os.sep)
            level = len(path_components)
            name = path_components[-1]

            # The path is already absolute
            item = DirectoryItem(path=path, level=level, name=name)
            structure.add_item(item)

        return structure