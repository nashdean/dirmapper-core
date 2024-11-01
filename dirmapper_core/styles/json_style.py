import os
from typing import List, Tuple
from dirmapper_core.styles.base_style import BaseStyle

class JSONStyle(BaseStyle):
    """
    JSONStyle is a concrete class that inherits from the BaseStyle class. It provides an implementation for the write_structure method that converts a directory structure into a JSON representation.
    """
    def write_structure(self, structure: List[Tuple[str, int, str]], **kwargs) -> dict:
        """
        Takes a list of tuples representing the directory structure and returns a JSON representation of the structure where keys are directory names and values are either the path to the file or a nested dictionary representing the subdirectory structure.

        Args:
            - structure (List[Tuple[str, int, str]]): A list of tuples where each tuple contains the path to the file or directory, the level of indentation, and the name of the file or directory.
        
        Returns:
            - dict: A JSON representation of the directory structure.
            
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
                {
                    'dir': {
                        'file1.txt': '/path/to/dir/file1.txt',
                        'file2.txt': '/path/to/dir/file2.txt',
                        'subdir': {
                            'file3.txt': '/path/to/dir/subdir/file3.txt'
                        }
                    }
                }
        """
        def build_json_structure(structure, level: int) -> Tuple[dict, int]:
            """
            Builds a nested dictionary representing the directory structure in JSON format.

            Args:
                - structure (List[Tuple[str, int, str]]): A list of tuples representing the directory structure.
                - level (int): The current level of indentation in the directory structure.
            
            Returns:
                - Tuple[dict, int]: A tuple containing the JSON representation of the directory structure and the index of the last item processed.
            
            Example:
                Parameters:
                    structure = [
                        ('/path/to/dir', 0, 'dir'),
                        ('/path/to/dir/file1.txt', 1, 'file1.txt'),
                        ('/path/to/dir/file2.txt', 1, 'file2.txt'),
                        ('/path/to/dir/subdir', 1, 'subdir'),
                        ('/path/to/dir/subdir/file3.txt', 2, 'file3.txt')
                    ]
                    level = 0
                Result:
                    {
                        'dir': {
                            'file1.txt': '/path/to/dir/file1.txt',
                            'file2.txt': '/path/to/dir/file2.txt',
                            'subdir': {
                                'file3.txt': '/path/to/dir/subdir/file3.txt'
                            }
                        }
                    }
            """
            result = {}
            i = 0
            while i < len(structure):
                item_path, item_level, item = structure[i]
                if item_level == level:
                    if os.path.isdir(item_path):
                        sub_structure, sub_items = build_json_structure(structure[i+1:], level + 1)
                        result[item] = sub_structure
                        i += sub_items
                    else:
                        result[item] = item_path
                elif item_level < level:
                    break
                i += 1
            return result, i

        json_structure, _ = build_json_structure(structure, 0)
        return json_structure
