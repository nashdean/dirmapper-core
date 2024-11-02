from importlib.metadata import version, PackageNotFoundError
import os

from dirmapper_core.ignore.ignore_list_reader import IgnoreListReader, SimpleIgnorePattern, RegexIgnorePattern

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