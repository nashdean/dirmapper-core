from typing import List, Tuple
from dirmapper_core.styles.base_style import BaseStyle

class FlatListStyle(BaseStyle):
    """
    FlatListStyle is a concrete class that inherits from the BaseStyle class. It provides an implementation for the write_structure method that converts a directory structure into a flat list representation.
    """
    #TODO: Update this method to work with the template summarizer; see tree_style for details
    def write_structure(self, structure: List[Tuple[str, int, str]], **kwargs) -> str:
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
