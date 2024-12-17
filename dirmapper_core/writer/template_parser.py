from typing import Optional
import yaml
import json
import os
import re
import datetime

from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.styles.base_style import BaseStyle
from dirmapper_core.styles.flat_list_style import FlatListStyle
from dirmapper_core.styles.indentation_style import IndentationStyle
from dirmapper_core.styles.json_style import JSONStyle
from dirmapper_core.styles.list_style import ListStyle
from dirmapper_core.styles.tree_style import TreeStyle
from dirmapper_core.utils.logger import logger

class TemplateParser:
    """
    Class to parse template files in YAML or JSON format or a formatted directory structure string into a dict object (template).
    """
    def __init__(self, template_file: str=None):
        """
        Initialize the TemplateParser object.

        Args:
            template_file (str): The path to the template file to parse.
        """
        self.template_file = template_file

    def template_to_directory_structure(self, template: dict) -> DirectoryStructure:
        """
        Convert a template to a DirectoryStructure object.

        Args:
            template (dict): The template to convert.

        Returns:
            DirectoryStructure: The converted directory structure.
        """
        def process_dict(current_dict: dict, current_path: str = "", level: int = 0) -> None:
            for key, value in current_dict.items():
                if not isinstance(value, dict):
                    continue

                # Build the full path for this item
                key = key.rstrip('/')  # Remove trailing slash
                path = os.path.join(current_path, key) if current_path else key

                # If this dict has __keys__, create a DirectoryItem
                if '__keys__' in value:
                    keys_dict = value['__keys__']
                    metadata = {
                        'type': keys_dict['meta'].get('type', 'file' if '.' in key else 'directory'),
                        'content': keys_dict['content'].get('content', None),
                        'summary': keys_dict['content'].get('content_summary'),
                        'short_summary': keys_dict['content'].get('short_summary'),
                        'tags': keys_dict['meta'].get('tags', [])
                    }
                    item = DirectoryItem(path, level, key, metadata)
                    structure.add_item(item)

                # Recursively process nested dictionaries
                process_dict(value, path, level + 1)

        structure = DirectoryStructure()
        process_dict(template, level=-1)
        return structure
    
    def parse_template(self) -> dict:
        """
        Depreciated method -- will be removed in v0.3.0. Use parse_from_template_file() instead.
        """
        logger.warning("The parse_template() method is deprecated and will be removed in v0.3.0. Use parse_from_template_file() instead.")
        if self.template_file:
            return self.parse_template_file()
        else:
            raise ValueError("No template file provided")

    def parse_from_template_file(self, template_file:Optional[str]=None) -> dict:
        """
        Parse the template file and return it as a dictionary.

        Args:
            template_file (Optional[str]): The path to the template file to parse.

        Returns:
            dict: The parsed template as a dictionary.

        Example:
            Parameters:
                template_file = 'template.yaml'

            Result:
                {
                    "meta": {
                        "version": "2.0",
                        "source": "dirmapper",
                        "author": "user",
                        "last_modified_by": "user",
                        "description": "No description provided",
                        "root_path": "/path/to/root",
                        "creation_date": "2021-09-01T12:00:00",
                        "last_modified": "2021-09-01T12:00:00"
                    },
                    "template": {
                        "dir1/": {
                            "__keys__""{
                                "meta": {...},
                                "content": {...}
                            },
                            "file1.txt": {
                                "__keys__""{
                                    "meta": {...},
                                    "content": {...}
                                }
                            },
                            "file2.txt": {
                                "__keys__""{
                                    "meta": {...},
                                    "content": {...}
                                }
                            },
                            "subdir1/": {
                                "__keys__""{
                                    "meta": {...},
                                    "content": {...}
                                },
                                "file3.txt": {
                                    "__keys__""{
                                        "meta": {...},
                                        "content": {...}
                                    }
                                }
                            }
                        }
                    }
                }
            
        """
        try:
            if not self.template_file and not template_file:
                raise ValueError("No template file provided.")
            if template_file:
                self.template_file = template_file
                logger.info(f"Set template file to {self.template_file}")

            with open(self.template_file, 'r') as f:
                if self.template_file.endswith('.yaml') or self.template_file.endswith('.yml'):
                    template = yaml.safe_load(f)
                elif self.template_file.endswith('.json'):
                    template = json.load(f)
                else:
                    raise ValueError("Unsupported template file format. Please use YAML or JSON.")
            
            # Add author, creation_date, and last_modified to meta if not present
            if 'meta' not in template:
                template['meta'] = {}
            if 'author' not in template['meta']:
                template['meta']['author'] = os.getlogin()
            if 'source' not in template['meta']:
                template['meta']['source'] = 'dirmapper'
            if 'creation_date' not in template['meta']:
                template['meta']['creation_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if 'last_modified' not in template['meta']:
                template['meta']['last_modified'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Validate the template
            self.validate_template(template)
            
            logger.info(f"Successfully parsed template from {self.template_file}")
        except ValueError as e:
            logger.error(f"Error parsing template from {self.template_file}: {e}")
            raise

        return template

    def validate_template(self, template: dict) -> None:
        """
        Validate the parsed template to ensure it meets the expected format.

        Args:
            template (dict): The parsed template to validate.

        Raises:
            ValueError: If the template is invalid.
        """
        if 'meta' not in template:
            raise ValueError("Template is missing 'meta' section.")
        if 'template' not in template:
            raise ValueError("Template is missing 'template' section.")
        
        meta = template['meta']
        if 'version' not in meta:
            raise ValueError("Template 'meta' section is missing 'version'.")
        if meta['version'] != '2.0':
            raise ValueError("Unsupported template version. Supported version is '1.1'.")
        
        # Additional meta validations if needed
        required_meta_fields = ['author', 'tool', 'creation_date', 'last_modified']
        for field in required_meta_fields:
            if field not in meta:
                raise ValueError(f"Template 'meta' section is missing '{field}'.")

        # Validate the structure of the template section
        def validate_structure(structure):
            if not isinstance(structure, dict):
                raise ValueError("Template 'template' section must be a dictionary.")
            for key, value in structure.items():
                if key.endswith('/'):
                    if not isinstance(value, dict):
                        raise ValueError(f"Directory '{key}' must contain a dictionary of its contents.")
                    validate_structure(value)
                else:
                    if not isinstance(value, dict):
                        raise ValueError(f"File '{key}' must be a dictionary with '__keys__' section.")
                    if '__keys__' not in value:
                        raise ValueError(f"File '{key}' must contain '__keys__' section.")

        validate_structure(template['template'])
    
    def parse_from_directory_structure(self, structure_str: str, existing_content:bool=False, generate_content:bool=False) -> dict:
        """
        Depreciated method -- will be removed in v0.3.0. Use parse_from_style() instead.
        """
        logger.warning("The parse_from_directory_structure() method is deprecated and will be removed in v0.3.0. Use parse_from_style() instead.")
        return self.parse_from_style(structure_str, existing_content, generate_content)

    def parse_from_style(self, structure_str: str, existing_content:bool=False, generate_content:bool=False) -> dict:
        """
        Parse the styled directory structure string and return it as a formatted Template dictionary object.

        Args:
            structure_str (str): The directory structure string to parse.
            existing_content (bool): Whether to include existing content in the template. Only applicable if root path in directory structure is an existing directory and files/folders already exist.
            generate_content (bool): Whether to generate content for files in the template. Used to generate content for files in the template with OpenAI's GPT-4.

        Returns:
            dict: The parsed directory structure as a dictionary in a structured reusable template.

        Example:
            structure_str =
                path/to/root 
                └── dir1/
                    ├── file1.txt
                    ├── file2.txt
                    └── subdir1/
                        └── file3.txt

            parsed_structure =
            {
                "meta": {
                    "version": "2.0",
                    "source": "dirmapper",
                    "license": "No license specified",
                    "root_path": "path/to/root",
                    "author": "user",
                    "last_modified_by": "user",
                    "description": "No description provided",
                    "creation_date": "2021-09-01T12:00:00",
                    "last_modified": "2021-09-01T12:00:00"
                },
                "template": {
                    "path/to/root/": {
                        "__keys__": {"meta": {...}, "content": {...}},
                        "dir1/": {
                            "__keys__": {"meta": {...}, "content": {...}},
                            "file1.txt": {"__keys__": {"meta": {...}, "content": {...}}},
                            "file2.txt": {"__keys__": {"meta": {...}, "content": {...}}},
                            "subdir1/": {
                                "__keys__": {"meta": {...}, "content": {...}},
                                "file3.txt": {"__keys__": {"meta": {...}, "content": {...}}}
                            }
                        }
                    }
                }
            }
        """
        lines = structure_str.strip().split('\n')

        # Detect style
        style = self._detect_style(lines)
        generic_structure = style.parse_from_style(structure_str)
        # generic_structure is now a DirectoryStructure object with absolute paths

        # Convert the DirectoryStructure into a template dict using JSONStyle
        # include_content=existing_content will cause JSONStyle to attempt to load content from files if they exist
        # generate_content=generate_content will cause JSONStyle to generate content via OpenAI if files don't exist
        template_json = JSONStyle.write_structure(
            generic_structure,
            root_dir=generic_structure.to_list()[0].path,  # The root path
            include_content=existing_content,
            generate_content=generate_content
        )

        # Wrap the template_dict with the required meta
        return {
            "meta": {
                "version": "2.0",
                "source": "dirmapper",
                "license": "No license specified",
                "author": os.getlogin(),
                "last_modified_by": os.getlogin(),
                "description": "No description provided",
                "root_path": generic_structure.to_list()[0].path,
                "creation_date": datetime.datetime.now().isoformat(),
                "last_modified": datetime.datetime.now().isoformat()
            },
            "template": template_json
        }

    def _detect_style(self, lines):
        """
        Detect the style of the directory structure based on the content.

        Args:
            lines (list): The lines of the directory structure string.

        Returns:
            str: The detected style (TreeStyle, ListStyle, FlatListStyle, IndentedTreeStyle, IndentedStyle).
        """
        for line in lines[1:]:
            line = line.rstrip('\n')
            if not line.strip():
                continue
            # Line starts with tree-drawing characters without leading spaces
            if re.search(r'^(├──|└──)', line):
                return TreeStyle
            # Line contains only words and numbers with varying levels of indentation
            elif re.search(r'^\s+\w+', line):
                return IndentationStyle
            # Line starts with '-' followed by a space
            elif re.match(r'^\s*-\s+', line):
                return ListStyle
            # Flat style: lines with paths without special formatting
            elif re.match(r'^\S+', line):
                return FlatListStyle
        raise ValueError("Unsupported directory structure style.")

    def _parse_style(self, lines, style: BaseStyle, existing_content:bool, generate_content:bool) -> tuple:
        """
        Parse a given style directory structure into JSON.

        Args:
            lines (list): The lines of the directory structure string.
            style (BaseStyle): The style of the directory structure.
            existing_content (bool): Whether to include existing content in the template. Only applicable if root path in directory structure is an existing directory and files/folders already exist.
            generate_content (bool): Whether to generate content for files in the template. Used to generate content for files in the template with OpenAI's GPT-4.

        Returns:
            tuple: (root_path_str, template_dict)
        """
        template = {}
        root_path = None

        try:
            generic_structure = style.parse_from_style(lines)
            template = JSONStyle.write_structure(generic_structure, generate_content=generate_content)
            root_path = generic_structure.items[0].path # Get the root path from the first item in the structure
        except Exception as e:
            logger.error(f"Error parsing directory structure from {style.__str__}: {e}")
        
        return root_path, template