import os
from typing import List
import re
from importlib import resources
from dirmapper_core.utils.logger import logger

class IgnorePattern:
    """
    Base class for ignore patterns.
    
    Attributes:
        pattern (str): The pattern to ignore.
    """
    def __init__(self, pattern: str):
        self.pattern = pattern

    def matches(self, path: str) -> bool:
        """
        Check if the given path matches the ignore pattern.
        
        Args:
            path (str): The path to check against the pattern.
        
        Returns:
            bool: True if the path matches the pattern, False otherwise.
        """
        raise NotImplementedError("Subclasses should implement this method.")

class SimpleIgnorePattern(IgnorePattern):
    """
    Class for simple ignore patterns.
    """
    def matches(self, path: str) -> bool:
        """
        Check if the given path contains the pattern.
        
        Args:
            path (str): The path to check.
        
        Returns:
            bool: True if the path contains the pattern, False otherwise.
        """
        return self.pattern in path

class RegexIgnorePattern(IgnorePattern):
    """
    Class for regex-based ignore patterns.
    
    Attributes:
        regex (Pattern): Compiled regex pattern.
    """
    def __init__(self, pattern: str):
        super().__init__(pattern)
        self.regex = re.compile(pattern)

    def matches(self, path: str) -> bool:
        """
        Check if the given path matches the regex pattern.
        
        Args:
            path (str): The path to check.
        
        Returns:
            bool: True if the path matches the regex pattern, False otherwise.
        """
        return bool(self.regex.search(path))

class IgnoreListReader:
    """
    Class to read ignore patterns from a file.
    """
    def read_ignore_list(self, ignore_file: str) -> List[IgnorePattern]:
        """
        Read ignore patterns from a file.
        
        Args:
            ignore_file (str): The file containing ignore patterns.
        
        Returns:
            List[IgnorePattern]: A list of ignore pattern objects.
        
        Raises:
            FileNotFoundError: If the ignore file is not found.

        Example:
            Parameters:
                ignore_file = '.mapping-ignore'
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
        with open(ignore_file, 'r') as f:
            lines = f.readlines()

        ignore_patterns = []
        for line in lines:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            if line.startswith('regex:'):
                ignore_patterns.append(RegexIgnorePattern(line[len('regex:'):]))
            else:
                ignore_patterns.append(SimpleIgnorePattern(line))

        return ignore_patterns

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