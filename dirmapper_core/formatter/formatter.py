import json
from abc import ABC, abstractmethod
from dirmapper_core.styles.tree_style import TreeStyle
from dirmapper_core.styles.html_style import HTMLStyle
from dirmapper_core.styles.json_style import JSONStyle
"""
formatter.py: Contains the Formatter abstract class and its concrete implementations

All formatters should return the data as a particular format (e.g., plain text, HTML, JSON, etc.).
This differs from the Style classes, which are responsible for generating the structure of the data.
"""

class Formatter(ABC):
    @abstractmethod
    def format(self, data, instructions=None) -> str:
        pass

class PlainTextFormatter(Formatter):
    def format(self, data: str, instructions:dict={'style':TreeStyle()}) -> str:
        style = instructions.get('style')
        if style:
            return style.write_structure(data)
        return data

#TODO: Move HTMLStyle logic to HTMLFormatter class
class HTMLFormatter(Formatter):
    def format(self, data: str, instructions=None) -> str:
        html_data = HTMLStyle().write_structure(data)
        return f"<html><body><pre>{html_data}</pre></body></html>"

class JSONFormatter(Formatter):
    def format(self, data: dict | list, instructions:dict={}) -> str:
        """
        Format the data as a JSON string.

        Args:
            data: The data to format as JSON.
            instructions: The instructions for formatting the data. Currently not used by the JSON formatter.
        """
        if isinstance(data, dict):
            return json.dumps(data, indent=4)
        elif isinstance(data, list):
            return json.dumps(JSONStyle().write_structure(data), indent=4)
        else:
            raise ValueError("Data must be a dictionary or a JSON string to format as JSON")

#TODO: Update to implement format based on the JSON data structure provided by TemplateParser
class MarkdownFormatter(Formatter):
    def format(self, data: str, instructions=None) -> str:
        # Implement markdown formatting logic - each folder is a header, each file is a list item
        return data

# class TabbedListFormatter(Formatter):
#     def format(self, data: str) -> str:
#         # Implement tabbed list formatting logic
#         return data

# class TableFormatter(Formatter):
#     def format(self, data: str) -> str:
#         # Implement table formatting logic
#         return data

# class BulletPointFormatter(Formatter):
#     def format(self, data: str) -> str:
#         # Implement bullet point formatting logic
#         return data

# class TreeFormatter(Formatter):
#     def format(self, data: str) -> str:
#         # Implement tree formatting logic
#         return data
