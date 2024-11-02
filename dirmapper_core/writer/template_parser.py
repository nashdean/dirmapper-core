import yaml
import json
import os
import re
import datetime

class TemplateParser:
    """
    Class to parse template files in YAML or JSON format.
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
            template_file = 'template.yaml'
            parsed_template = {
                "meta": {
                    "version": "1.1",
                    "tool": "dirmapper",
                    "author": "user",
                    "creation_date": "2021-09-01T12:00:00",
                    "last_modified": "2021-09-01T12:00:00"
                },
                "template": {
                    "dir1": {
                        "file1.txt": {},
                        "file2.txt": {},
                        "subdir1": {
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
    
    def parse_directory_structure(self, structure_str: str) -> dict:
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
                    "dir1": {
                        "file1.txt": {},
                        "file2.txt": {},
                        "subdir1": {
                            "file3.txt": {}
                        }
                    }
                }
            }
        """
        lines = structure_str.strip().split('\n')
        root = {}
        stack = [(root, -1)]  # Stack of (current_node, indent_level)

        for line in lines:
            if not line.strip():
                continue

            # Calculate indent level based on leading tree characters
            indent_match = re.match(r'^(│   )*', line)
            indent_str = indent_match.group(0) if indent_match else ''
            indent_level = indent_str.count('│   ')

            # Remove leading indentation and tree mapping characters
            name = line[len(indent_str):].strip()
            name = re.sub(r'^(├── |└── )', '', name).strip()

            # Check if it's a directory (ends with '/') or a file
            is_dir = name.endswith('/')
            # if is_dir:
            #     name = name.rstrip('/')

            # Create a new node
            new_node = {} if is_dir else {}

            # Adjust the stack based on the current indentation level
            while stack and stack[-1][1] >= indent_level:
                stack.pop()

            # Add the new node to its parent in the stack
            parent_node, _ = stack[-1]
            parent_node[name] = new_node

            # If it's a directory, push it onto the stack
            if is_dir:
                stack.append((new_node, indent_level))

        # Wrap the root in a template with metadata
        return {
            "meta": {
                "version": "1.1",
                "tool": "dirmapper",
                "author": os.getlogin(),
                "creation_date": datetime.datetime.now().isoformat(),
                "last_modified": datetime.datetime.now().isoformat()
            },
            "template": root
        }
