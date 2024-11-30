import os
from typing import List, Tuple
from dirmapper_core.styles.base_style import BaseStyle

class FlatListStyle(BaseStyle):
    """
    FlatListStyle is a concrete class that inherits from the BaseStyle class. It provides an implementation for the write_structure method that converts a directory structure into a flat list representation.
    """
    #TODO: Update this method to work with the template summarizer; see tree_style for details
    def write_structure(structure: List[Tuple[str, int, str]], **kwargs) -> str:
        """
        Takes a list of tuples representing the directory structure and returns a flat list representation of the structure.

        Args:
            - structure (List[Tuple[str, int, str]]): A list of tuples where each tuple contains the path to the file or directory, the level of indentation, and the name of the file or directory.

        Returns:
            - str: A flat list representation of the directory structure.

        Example:
            Parameters:
                structure =
                [
                    ('/path/to/dir', 0, 'dir'),
                    ('/path/to/dir/file1.txt', 1, 'file1.txt'),
                    ('/path/to/dir/file2.txt', 1, 'file2.txt'),
                    ('/path/to/dir/subdir', 1, 'subdir'),
                    ('/path/to/dir/subdir/file3.txt', 2, 'file3.txt')
                ]

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
    def parse_from_style(flat_list_str: str, root_dir: str = "") -> List[Tuple[str, int, str]]:
        """
        Parse a flat list of paths back into a list of tuples representing the
        directory structure.

        Args:
            flat_list_str (str): The flat list of paths, one per line.
            root_dir (str): Optional root directory path. If not provided, the
                            first path in the list is considered the root.

        Returns:
            List[Tuple[str, int, str]]: A list of tuples representing the
                                        directory structure.
        """
        lines = flat_list_str.strip().splitlines()
        if not lines:
            return []

        structure = []

        # Identify the root directory
        root_path = lines[0].strip()
        root_dir = root_dir or root_path  # Use provided root_dir or root_path

        # Add the root directory to the structure
        structure.append((root_path, 0, root_path))

        for line in lines[1:]:
            path = line.strip()
            # Calculate the relative path to the root directory
            relative_path = os.path.relpath(path, start=root_dir)
            # Split the relative path into components
            path_components = relative_path.split(os.sep)
            level = len(path_components)
            name = path_components[-1]

            # Reconstruct the relative path for the structure
            reconstructed_path = os.path.join(*path_components)

            structure.append((reconstructed_path, level, name))

        return structure