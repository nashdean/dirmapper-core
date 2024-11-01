# dirmapper/utils/cli_utils.py

from importlib.metadata import version, PackageNotFoundError
import os

from openai import AuthenticationError, OpenAI
from dirmapper_core.ignore.ignore_list_reader import IgnoreListReader, SimpleIgnorePattern, RegexIgnorePattern
from typing import List, Tuple
from importlib import resources

from dirmapper_core.utils.logger import log_exception, logger

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

def read_ignore_patterns(ignore_file: str, include_gitignore: bool, additional_ignores: List[str]) -> List:
    """
    Reads ignore patterns from the specified ignore file and optionally includes patterns from .gitignore.

    Args:
        ignore_file (str): The path to the ignore file listing directories and files to ignore.
        include_gitignore (bool): Flag indicating whether to include patterns from .gitignore.
        additional_ignores (list): Additional patterns to ignore specified at runtime.

    Returns:
        list: A list of IgnorePattern objects.
    
    Raises:
        FileNotFoundError: If the ignore file is not found.
    
    Example:
        Parameters:
            ignore_file = '.mapping-ignore'
            include_gitignore = True
            additional_ignores = ['regex:.*\.log']
        Result:
            ignore_patterns = [
                SimpleIgnorePattern('node_modules'),
                SimpleIgnorePattern('build'),
                SimpleIgnorePattern('.git'),
                SimpleIgnorePattern('.mapping'),
                SimpleIgnorePattern('.mapping-ignore'),
                RegexIgnorePattern('.*\.log')
            ]
    """
    ignore_list_reader = IgnoreListReader()
    ignore_patterns = []

    # Read ignore patterns from the specified ignore file
    try:
        ignore_patterns.extend(ignore_list_reader.read_ignore_list(ignore_file))
    except FileNotFoundError as e:
        if ignore_file == '.mapping-ignore':
            # Try to read default .mapping-ignore from package data
            try:
                with resources.open_text('dirmapper_core.data', '.mapping-ignore') as f:
                    patterns = f.read().splitlines()
                # Convert patterns to IgnorePattern objects
                for pattern in patterns:
                    pattern = pattern.strip()
                    if not pattern or pattern.startswith('#'):
                        continue  # Skip empty lines and comments
                    if pattern.startswith('regex:'):
                        ignore_patterns.append(RegexIgnorePattern(pattern[len('regex:'):]))
                    else:
                        ignore_patterns.append(SimpleIgnorePattern(pattern))
            except Exception as pkg_e:
                logger.error(f"Could not read default .mapping-ignore from package data: {pkg_e}")
                raise pkg_e
        else:
            # Re-raise the original exception
            raise e

    # Read patterns from .gitignore if requested
    if include_gitignore:
        try:
            gitignore_patterns = ignore_list_reader.read_ignore_list('.gitignore')
            ignore_patterns.extend(gitignore_patterns)
        except FileNotFoundError:
            # If .gitignore not found, skip it
            pass

    # Add additional ignore patterns from the command line
    for pattern in additional_ignores:
        if pattern.startswith('regex:'):
            ignore_patterns.append(RegexIgnorePattern(pattern[len('regex:'):]))
        else:
            ignore_patterns.append(SimpleIgnorePattern(pattern))

    return ignore_patterns

def parse_sort_argument(sort_arg: str) -> Tuple[str, bool]:
    """
    Parses the sort argument to determine the sorting strategy and case sensitivity.

    Args:
        sort_arg (str): The sort argument in the format 'asc', 'asc:case', 'desc', or 'desc:case'.

    Returns:
        tuple: A tuple containing the sort order and case sensitivity flag.
    """
    if sort_arg is None:
        return None, False
    
    parts = sort_arg.split(':')
    sort_order = parts[0]
    case_sensitive = True if len(parts) > 1 and parts[1] == 'case' else False
    return sort_order, case_sensitive

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