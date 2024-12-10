from importlib.metadata import version, PackageNotFoundError
import os
from typing import List

from dirmapper_core.ignore.ignore_list_reader import IgnoreListReader, SimpleIgnorePattern, RegexIgnorePattern
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure

def clean_json_keys(data: dict | list) -> dict:
    """
    Recursively clean the keys of a JSON-like data structure by removing tree drawing characters. Useful for removing the tree drawing characters from keys of a directory structure template.

    Args:
        data (dict | list): The JSON-like data structure to clean.
    
    Returns:
        dict: The cleaned data structure.
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # Remove tree drawing characters from the key
            clean_key = key.replace('├── ', '').replace('└── ', '').replace('│   ', '').strip()
            # Recursively clean the value
            new_dict[clean_key] = clean_json_keys(value)
        return new_dict
    elif isinstance(data, list):
        return [clean_json_keys(item) for item in data]
    else:
        # Base case: return the data as is
        return data

def get_package_version(package_name: str) -> str:
    """
    Get the version of the specified package.

    Args:
        package_name (str): The name of the package to get the version of.
    
    Returns:
        str: The version of the package.
    
    Raises:
        PackageNotFoundError: If the package is not found.
    
    Example:
        Parameters:
            package_name = 'dirmapper-core'
        Result:
            version = '0.0.3'
    """
    
    # Check if version is passed via environment variable (for Homebrew)
    ver = os.getenv("DIRMAPPER_VERSION")
    if ver:
        return ver
    
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown version"

def is_last_item(structure: List[DirectoryItem], index: int, current_level: int) -> bool:
    """
    Determine if the current item is the last one at its level in the structure.

    Args:
        structure (list): A list of tuples representing the directory structure.
                        Each tuple contains (item_path, level, item).
        index (int): The index of the current item in the structure list.
        current_level (int): The level of the current item in the directory structure.

    Returns:
        bool: True if the current item is the last one at its level, False otherwise.

    Example:
        structure = [
            DirectoryItem('/path/to/root/dir', 0, 'root'),
            DirectoryItem('file1.txt', 1, 'file1.txt'),
            DirectoryItem('file2.txt', 1, 'file2.txt'),
            DirectoryItem('sub_dir1', 1, 'sub_dir1'),
            DirectoryItem('sub_dir1/sub_dir2', 2, 'sub_dir2'),
            DirectoryItem('sub_dir1/sub_dir2/file3.txt', 3, 'file3.txt'),
            DirectoryItem('sub_dir1/sub_dir2/file4.txt', 3, 'file4.txt'),
            DirectoryItem('sub_dir3', 1, 'sub_dir3'),
            DirectoryItem('sub_dir3/file5.txt', 2, 'file5.txt')
        ]
        index = 1
        current_level = 1
        is_last_item(structure, index, current_level)  # Returns False
    """
    # Check if there is any next item at the same level
    for next_index in range(index + 1, len(structure)):
        next_level = structure[next_index].level
        if next_level == current_level:
            return False  # There is another item at the same level
        elif next_level < current_level:
            break
    return True  # No more items at the same level

def is_directory(item):
    """
    Determine if the item is a directory.
    """
    # Assuming directories are marked with a trailing '/'
    return item.endswith('/')