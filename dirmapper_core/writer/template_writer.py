import json
import os
import yaml

from dirmapper_core.writer.template_parser import TemplateParser
from dirmapper_core.utils.logger import logger


def write_template(template_path: str, structure: dict | str, create_missing_folders: bool = True) -> None:
    """
    Write the generated directory structure to a template file to your OS.

    Args:
        template_path (str): The path to write the template file to.
        structure (dict): The directory structure to write to the template file.
        create_missing_folders (bool): Flag indicating whether to create missing folders in the path. Defaults to True.
    """
    try:
        template_path = os.path.expanduser(template_path)
        if not template_path.endswith('.json') and not template_path.endswith('.yaml') and not template_path.endswith('.yml'):
            template_path += '.json'  # Default to JSON if no valid extension is provided
        
        # Create the directory if it doesn't exist and create_missing_folders is True
        if create_missing_folders:
            directory = os.path.dirname(template_path)
            if not directory:
                directory = os.getcwd()  # Set default directory to current working directory
            os.makedirs(directory, exist_ok=True)

        if isinstance(structure, str):
            tp = TemplateParser()
            structure = tp.parse_from_style(structure)

        with open(template_path, 'w') as template_file:
            if template_path.endswith('.yaml') or template_path.endswith('.yml'):
                yaml.dump(structure, template_file, default_flow_style=False)
            else:
                json.dump(structure, template_file, indent=4)
        logger.info(f"Template file created at {os.path.abspath(template_path)}")
    except FileNotFoundError:
        logger.error(f"Error writing template file to {os.path.abspath(template_path)}. Please check the directory path exists.")