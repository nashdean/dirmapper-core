# directory_structure_generator.py

import os
import sys
from typing import List, Tuple
from dirmapper_core.utils.logger import log_exception, logger, log_ignored_paths
from dirmapper_core.sort.sorting_strategy import SortingStrategy
from dirmapper_core.ignore.path_ignorer import PathIgnorer
from dirmapper_core.utils.constants import STYLE_MAP, EXTENSIONS, FORMATTER_MAP
from dirmapper_core.styles.base_style import BaseStyle
from dirmapper_core.formatter.formatter import Formatter

class DirectoryStructureGenerator:
    """
    Class to generate a directory structure mapping.
    
    Attributes:
        root_dir (str): The root directory to map.
        output (str): The output file to save the directory structure.
        ignorer (PathIgnorer): Object to handle path ignoring.
        sort_order (str): The order to sort the directory structure ('asc', 'desc', or None).
        style (BaseStyle): The style to use for the directory structure output.
        formatter (Formatter): The formatter to use for the directory structure output.
        sorting_strategy (SortingStrategy): The strategy to use for sorting.
        max_depth (int): The maximum depth to traverse in the directory structure.
    """
    def __init__(self, root_dir: str, output: str, ignorer: PathIgnorer, sorting_strategy: SortingStrategy, case_sensitive: bool = True, style: BaseStyle = None, formatter: Formatter = None, max_depth: int = 5):
        self.root_dir = os.path.expanduser(root_dir)
        self.output = output
        self.ignorer = ignorer
        self.sorting_strategy = sorting_strategy
        self.style = style if style else STYLE_MAP['tree']()
        self.formatter = formatter if formatter else FORMATTER_MAP['plain']()
        self.max_depth = max_depth

        if output:
            self._validate_file_extension()

        logger.info(f"Directory structure generator initialized for root dir: {root_dir}, output file: {output}, style: {self.style.__class__.__name__}, formatter: {self.formatter.__class__.__name__}")

    def generate(self) -> str:
        """
        Generate the directory structure and returns it as a string.
        
        Raises:
            NotADirectoryError: If the root directory is not valid.
            Exception: If any other error occurs during generation.
        """
        try:
            if not self.verify_path(self.root_dir):
                raise NotADirectoryError(f'"{self.root_dir}" is not a valid path to a directory.')
            logger.info(f"Generating directory structure...")

            sorted_structure = self._build_sorted_structure(self.root_dir, level=0)

            instructions = {'style': self.style}
            formatted_structure = self.formatter.format(sorted_structure, instructions)

            # Log the ignored paths after generating the directory structure
            log_ignored_paths(self.ignorer)

            return formatted_structure

        except NotADirectoryError as e:
            log_exception(os.path.basename(__file__), e)
            sys.exit(1)
        except Exception as e:
            log_exception(os.path.basename(__file__), e)
            print(f"Error: {e}")

    def _build_sorted_structure(self, current_dir: str, level: int) -> List[Tuple[str, int, str]]:
        """
        Build the sorted directory structure.
        
        Args:
            current_dir (str): The current directory to build the structure from.
            level (int): The current level of depth in the directory structure.
        
        Returns:
            List[Tuple[str, int, str]]: The sorted directory structure.
        """
        structure = []
        dir_contents = os.listdir(current_dir)
        sorted_contents = self.sorting_strategy.sort(dir_contents)
        
        if level > self.max_depth:
            # Use relative path
            relative_path = os.path.relpath(current_dir, self.root_dir)
            structure.append((os.path.join(relative_path, ". . ."), level, ". . ."))
            return structure
        
        for item in sorted_contents:
            item_path = os.path.join(current_dir, item)
            if self.ignorer.should_ignore(item_path):
                continue
            # Compute relative path
            relative_item_path = os.path.relpath(item_path, self.root_dir)
            structure.append((relative_item_path, level, item))

            if os.path.isdir(item_path):
                structure.extend(self._build_sorted_structure(item_path, level + 1))

        return structure

    def _validate_file_extension(self) -> None:
        """
        Validate the output file extension based on the selected style.
        
        Raises:
            ValueError: If the output file extension does not match the expected extension for the selected style.
        """
        style_name = self.style.__class__.__name__.lower().replace('style', '')
        expected_extension = EXTENSIONS.get(style_name, '.txt')
        if not self.output.endswith(expected_extension):
            raise ValueError(f"Output file '{self.output}' does not match the expected extension for style '{self.style.__class__.__name__}': {expected_extension}")

    def verify_path(self, path: str = None) -> bool:
        """
        Verify if a path is a valid directory.
        
        Args:
            path (str): The path to verify.
        
        Returns:
            bool: True if the path is a valid directory, False otherwise.
        """
        if path:
            expanded_path = os.path.expanduser(str(path))
        else:
            expanded_path = os.path.expanduser(str(self.root_dir))
        return os.path.isdir(expanded_path)
