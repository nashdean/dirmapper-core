import json
import os
import yaml

from dirmapper_core.utils.logger import logger

def write_template(template_path, structure):
    """
    Write the generated directory structure to a template file.
    """
    if not template_path.endswith('.json') and not template_path.endswith('.yaml') and not template_path.endswith('.yml'):
        template_path += '.json'  # Default to JSON if no valid extension is provided
    
    with open(template_path, 'w') as template_file:
        if template_path.endswith('.yaml') or template_path.endswith('.yml'):
            yaml.dump(structure, template_file, default_flow_style=False)
        else:
            json.dump(structure, template_file, indent=4)
    logger.info(f"Template file created at {template_path}")