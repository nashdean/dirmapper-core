# directory_structure_generator.py

import os
import sys
from typing import List, Optional, Tuple
from dirmapper_core.utils.logger import log_exception, logger, log_ignored_paths
from dirmapper_core.sort.sorting_strategy import NoSortStrategy, SortingStrategy
from dirmapper_core.ignore.path_ignorer import PathIgnorer
from dirmapper_core.utils.constants import STYLE_MAP, EXTENSIONS, FORMATTER_MAP
from dirmapper_core.styles.base_style import BaseStyle
from dirmapper_core.formatter.base_formatter import BaseFormatter

from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.models.directory_item import DirectoryItem

class DirectoryStructureGenerator:
    """
    Class to generate a directory structure mapping.
    
    Attributes:
        root_dir (str): The root directory to map.
        ignorer (PathIgnorer): Object to handle path ignoring.
        sorting_strategy (SortingStrategy): The order to sort the directory structure.
        style (BaseStyle): The style to use for the directory structure output.
        formatter (BaseFormatter): The formatter to use for the directory structure output.
        max_depth (int): The maximum depth to traverse in the directory structure.
    """
    def __init__(self, root_dir: str, ignorer: Optional[PathIgnorer] = None, sorting_strategy: SortingStrategy = NoSortStrategy(), style: Optional[BaseStyle] = None, formatter: Optional[BaseFormatter] = None, max_depth: int = 5):
        self.root_dir = os.path.expanduser(root_dir)
        self.ignorer = ignorer
        self.sorting_strategy = sorting_strategy
        self.style = style if style else STYLE_MAP['tree']
        self.formatter = formatter if formatter else FORMATTER_MAP['plain']()
        self.max_depth = max_depth

        logger.debug(f"Directory structure generator initialized for root dir: {root_dir}, style: {self.style.__class__.__name__}, formatter: {self.formatter.__class__.__name__}, max depth: {max_depth}")

    def generate(self, file_output: Optional[str] = None, styled: bool = True, **kwargs) -> str | dict | DirectoryStructure:
        """
        Generate the directory structure and returns it as a string or JSON template depending on the DirectoryStructureGenerator selected `style` input.
        
        Args:
            file_output (str): The file to save the directory structure to.
            styled (bool): Whether to return the styled output (True) or the raw output (False).

        Raises:
            NotADirectoryError: If the root directory is not valid.
            Exception: If any other error occurs during generation.
        """
        try:
            if not self._verify_path(self.root_dir):
                raise NotADirectoryError(f'"{self.root_dir}" is not a valid path to a directory.')
            logger.info(f"Generating directory structure...")

            # Start with the root directory
            structure = DirectoryStructure()
            root_name = os.path.abspath(self.root_dir)  # Get the absolute path
            structure.add_item(DirectoryItem(root_name, 0, root_name))

            sorted_structure = self._build_sorted_structure(self.root_dir, level=1)
            structure.items.extend(sorted_structure.to_list())
            
            # Format the directory structure based on the selected style
            if styled:
                instructions = {
                    'style': self.style,
                    'root_dir': self.root_dir,  # Include root_dir in instructions
                }
                instructions.update(kwargs)  # Include any additional kwargs in instructions
                formatted_structure = self.formatter.format(structure, instructions) # Return the formatted structure as a string (or dict if JSON)
            else:
                formatted_structure = structure # Return the raw structure as DirectoryStructure object

            # Log the ignored paths after generating the directory structure
            log_ignored_paths(self.ignorer)

            if file_output:
                self._validate_file_extension()
                with open(file_output, 'w') as f:
                    f.write(formatted_structure)
                logger.info(f"Directory structure saved to {file_output}")


            return formatted_structure

        except NotADirectoryError as e:
            log_exception(os.path.basename(__file__), e)
            sys.exit(1)
        except ValueError as e:
            log_exception(os.path.basename(__file__), e)
            sys.exit(1)
        except Exception as e:
            log_exception(os.path.basename(__file__), e)
            sys.exit(1)

    def _build_sorted_structure(self, current_dir: str, level: int) -> DirectoryStructure:
        """
        Build the sorted directory structure.
        
        Args:
            current_dir (str): The current directory to build the structure from.
            level (int): The current level of depth in the directory structure.
        
        Returns:
            DirectoryStructure: The sorted directory structure.
        """
        structure = DirectoryStructure()
        dir_contents = os.listdir(current_dir)
        sorted_contents = self.sorting_strategy.sort(dir_contents)
        
        if level > self.max_depth:
            relative_path = os.path.relpath(current_dir, self.root_dir)
            structure.add_item(DirectoryItem(os.path.join(current_dir, ". . ."), level, ". . ."))
            return structure
        
        for item in sorted_contents:
            item_path = os.path.join(current_dir, item)
            if self.ignorer.should_ignore(item_path):
                continue
            metadata = {}
            if os.path.isfile(item_path):
                metadata['content'] = None  # Indicate that content is available but not loaded
            structure.add_item(DirectoryItem(item_path, level, item, metadata))

            if os.path.isdir(item_path):
                sub_structure = self._build_sorted_structure(item_path, level + 1)
                structure.items.extend(sub_structure.to_list())

        return structure

    def _validate_file_extension(self, output) -> None:
        """
        Validate the output file extension based on the selected style.
        
        Args:
            output (str): The output file to validate.

        Raises:
            ValueError: If the output file extension does not match the expected extension for the selected style.
        """
        style_name = self.style.__class__.__name__.lower().replace('style', '')
        expected_extension = EXTENSIONS.get(style_name, '.txt')
        if not output.endswith(expected_extension):
            raise ValueError(f"Output file '{output}' does not match the expected extension for style '{self.style.__class__.__name__}': {expected_extension}")

    def _verify_path(self, path: str = None) -> bool:
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
