import logging
import yaml
import json
import os
import re
import datetime

from dirmapper_core.styles.base_style import BaseStyle
from dirmapper_core.styles.flat_list_style import FlatListStyle
from dirmapper_core.styles.indentation_style import IndentationStyle
from dirmapper_core.styles.indented_tree_style import IndentedTreeStyle
from dirmapper_core.styles.json_style import JSONStyle
from dirmapper_core.styles.list_style import ListStyle
from dirmapper_core.styles.tree_style import TreeStyle

class TemplateParser:
    """
    Class to parse template files in YAML or JSON format or a formatted directory structure string into a dict object.
    """
    def __init__(self, template_file: str=None):
        """
        Initialize the TemplateParser object.

        Args:
            template_file (str): The path to the template file to parse.
        """
        self.template_file = template_file

    def parse_template(self) -> dict:
        """
        Parse the template file and return it as a dictionary.

        Returns:
            dict: The parsed template as a dictionary.

        Example:
            Parameters:
                template_file = 'template.yaml'

            Result:
                {
                    "meta": {
                        "version": "1.1",
                        "tool": "dirmapper",
                        "author": "user",
                        "creation_date": "2021-09-01T12:00:00",
                        "last_modified": "2021-09-01T12:00:00"
                    },
                    "template": {
                        "dir1/": {
                            "file1.txt": {},
                            "file2.txt": {},
                            "subdir1/": {
                                "file3.txt": {}
                            }
                        }
                    }
                }
            
        """
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
        if 'tool' not in template['meta']:
            template['meta']['tool'] = 'dirmapper'
        if 'creation_date' not in template['meta']:
            template['meta']['creation_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'last_modified' not in template['meta']:
            template['meta']['last_modified'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return template
    
    def parse_from_directory_structure(self, structure_str: str) -> dict:
        """
        Parse the directory structure string and return it as a dictionary.

        Args:
            structure_str (str): The directory structure string to parse.

        Returns:
            dict: The parsed directory structure as a dictionary in a structured reusable template.

        Example:
            structure_str = 
                dir1/
                ├── file1.txt
                ├── file2.txt
                └── subdir1/
                    └── file3.txt

            parsed_structure =
            {
                "meta": {
                    "version": "1.1",
                    "tool": "dirmapper",
                    "author": "user",
                    "creation_date": "2021-09-01T12:00:00",
                    "last_modified": "2021-09-01T12:00:00"
                },
                "template": {
                    "dir1/": {
                        "file1.txt": {},
                        "file2.txt": {},
                        "subdir1/": {
                            "file3.txt": {}
                        }
                    }
                }
            }
        """
        lines = structure_str.strip().split('\n')

        # Detect style
        style = self._detect_style(lines)
        root_path, template = self._parse_style(structure_str, style)

        # Wrap the template with metadata
        return {
            "meta": {
                "version": "1.1",
                "tool": "dirmapper",
                "author": os.getlogin(),
                "root_path": root_path,
                "creation_date": datetime.datetime.now().isoformat(),
                "last_modified": datetime.datetime.now().isoformat()
            },
            "template": template
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
            # Line starts with spaces followed by tree-drawing characters
            elif re.search(r'^\s+(├──|└──)', line):
                return IndentedTreeStyle
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

    def _parse_style(self, lines, style: BaseStyle):
        """
        Parse a given style directory structure into JSON.

        Args:
            lines (list): The lines of the directory structure string.

        Returns:
            tuple: (root_path, template_dict)
        """
        template = {}
        root_path = None

        # try:
        #TODO: There is a bug here where the relative path is not parsing correctly over to the JSONStyle for files/folders
        generic_structure = style.parse_from_style(lines)
        template = JSONStyle.write_structure(generic_structure)
        root_path = generic_structure[0][0] # Get the root path from the first item in the structure
        # except Exception as e:
        #     logging.error(f"Error parsing directory structure from {style.__STR__}: {e}")
        
        return root_path, template

    def _parse_tree_style(self, lines):
        """
        Parse the tree style directory structure.
        """
        template = {}
        stack = []  # Stack of (parent_node, depth)

        root_path = None

        for line in lines:
            if not line.strip():
                continue

            # Detect the root path (first line without any indentation or connectors)
            if root_path is None and not re.match(r'^\s*[├└│]', line):
                root_path = line.strip()
                continue

            # Get depth and name
            depth, name = self._get_depth_and_name(line)

            # Adjust the stack based on the current depth
            while len(stack) > depth:
                stack.pop()

            # Create a new node
            is_dir = name.endswith('/')
            new_node = {} if is_dir else {}

            if depth == 0:
                # At root level
                template[name] = new_node
                if is_dir:
                    stack.append((template[name], depth))
            else:
                if stack:
                    parent_node = stack[-1][0]
                    parent_node[name] = new_node
                    if is_dir:
                        stack.append((parent_node[name], depth))
                else:
                    # Should not happen, but just in case
                    template[name] = new_node
                    if is_dir:
                        stack.append((template[name], depth))

        return root_path, template

    def _get_depth_and_name(self, line):
        """
        Extract the depth and name from a line in the tree structure.
        """
        pattern = r'^(?P<indent>(?:    |│   )*)(?:[├└][─]{2} )?(?P<name>.*)'
        match = re.match(pattern, line)
        if match:
            indent = match.group('indent')
            name = match.group('name').strip()
            # Calculate depth
            depth = 0
            index = 0
            while index < len(indent):
                chunk = indent[index:index+4]
                if chunk in ('    ', '│   '):
                    depth +=1
                    index +=4
                else:
                    break
            return depth, name
        else:
            # Line does not match expected pattern
            return 0, line.strip()
    
    def _parse_indented_tree_style(self, lines):
        """
        Parse the indented tree style directory structure.

        Args:
            lines (list): The lines of the directory structure string.

        Returns:
            tuple: (root_path, template_dict)
        """
        template = {}
        stack = []  # Stack of (parent_node, depth)
        root_path = None

        for line in lines:
            if not line.strip():
                continue

            # Detect the root path (first line without indentation)
            if root_path is None and not line.startswith((' ', '\t')):
                root_path = line.strip()
                continue

            # Get depth and name
            depth, name = self._get_indented_depth_and_name(line)

            # Determine if it's a directory (ends with '/')
            is_dir = name.endswith('/')

            # Create a new node
            new_node = {} if is_dir else {}

            # Adjust the stack based on the current depth
            while len(stack) and stack[-1][1] >= depth:
                stack.pop()

            if stack:
                parent_node = stack[-1][0]
                parent_node[name] = new_node
            else:
                template[name] = new_node

            if is_dir:
                stack.append((new_node, depth))

        return root_path, template

    def _get_indented_depth_and_name(self, line):
        """
        Extract the depth and name from a line in the indented tree structure.

        Args:
            line (str): A line from the directory structure string.

        Returns:
            tuple: (depth, name)
        """
        # Replace tabs with 4 spaces
        line = line.replace('\t', '    ')

        # Count the number of leading spaces
        leading_spaces = len(line) - len(line.lstrip(' '))

        # Calculate depth (assuming 4 spaces per indent level)
        depth = leading_spaces // 4

        # Remove leading spaces
        line = line.lstrip(' ')

        # Remove any tree-drawing characters and spaces at the beginning
        line = re.sub(r'^[│├└─\s]+', '', line)

        name = line.strip()

        return depth, name

    def _parse_indentation_style(self, lines):
        """
        Parse the indentation style directory structure.
        """
        template = {}
        stack = []
        root_path = None

        for line in lines:
            if not line.strip():
                continue

            # Detect the root path (first line without indentation)
            if root_path is None and not line.startswith((' ', '\t')):
                root_path = line.strip()
                continue

            # Compute depth
            leading_spaces = len(line) - len(line.lstrip(' '))
            depth = leading_spaces // 4

            # Get name
            name = line.strip()

            if not name:
                continue  # Skip empty names

            # Adjust the stack based on the current depth
            while len(stack) > depth:
                stack.pop()

            new_node = {}

            if len(stack) == 0:
                # At root level
                template[name] = new_node
                stack.append((template[name], depth))
            else:
                parent_node = stack[-1][0]
                parent_node[name] = new_node
                stack.append((parent_node[name], depth))

        return root_path, template

    def _parse_list_style(self, lines):
        """
        Parse the list style directory structure.

        Args:
            lines (list): The lines of the directory structure string.

        Returns:
            tuple: (root_path, template_dict)
        """
        template = {}
        stack = []  # Stack of (parent_node, depth)
        root_path = None

        for line in lines:
            if not line.strip():
                continue
            
            # Detect the root path (first line without indentation)
            if root_path is None and not line.startswith((' ', '\t')):
                root_path = line.strip()
                continue

            # Match lines that start with optional spaces, a dash, and a space
            match = re.match(r'^(?P<indent>\s*)-\s+(?P<name>.*)', line)
            if not match:
                continue  # Skip lines that don't match

            indent_str = match.group('indent')
            name = match.group('name').strip()

            depth = len(indent_str) // 4  # Assuming 4 spaces per indent

            # Adjust the stack based on the current depth
            while len(stack) > depth:
                stack.pop()

            # Create a new node
            new_node = {}

            if stack:
                parent_node = stack[-1][0]
                parent_node[name] = new_node
            else:
                template[name] = new_node

            # Push the new node and its depth onto the stack
            stack.append((new_node, depth))

        return root_path, template

    def _parse_flat_style(self, lines):
        """
        Parse the flat style directory structure.

        Args:
            lines (list): The lines of the directory structure string.

        Returns:
            tuple: (root_path, template_dict)
        """
        template = {}
        root_path = None

        # Check if the first line is an absolute path
        if lines and lines[0].startswith('/'):
            root_path = lines[0].strip()
            lines = lines[1:]  # Remove the root path from the lines
        else:
            root_path = '/'

        for line in lines:
            if not line.strip():
                continue

            path = line.strip()
            parts = path.strip('/').split('/')

            if not parts:
                continue

            current_node = template
            for i, part in enumerate(parts):
                is_dir = (i < len(parts) - 1) or path.endswith('/')
                part_name = part + '/' if is_dir else part

                if part_name not in current_node:
                    current_node[part_name] = {}
                current_node = current_node[part_name]

        return root_path, template
