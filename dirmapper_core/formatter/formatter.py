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
    """
    Abstract class for formatters. Formatters are responsible for converting data into a specific format (e.g., plain text, HTML, JSON, etc.).
    """
    @abstractmethod
    def format(self, data, instructions=None) -> str:
        """
        Abstract method to format the data into a specific format.
        """
        pass

class PlainTextFormatter(Formatter):
    """
    A concrete implementation of the Formatter class that formats data as plain text.
    """
    def format(self, data: str, instructions:dict={'style':TreeStyle()}) -> str:
        """
        Format the data as plain text.

        Args:
            data (str): The data to format as plain text.
            instructions (dict): The instructions for formatting the data. The instructions should include a 'style' key that specifies the style to use for formatting the data. Defaults to TreeStyle.
        
        Returns:
            str: The data formatted as plain text.
        
        Example:
            Parameters:
                data = [
                    ('/path/to/dir', 0, 'dir'),
                    ('/path/to/dir/file1.txt', 1, 'file1.txt'),
                    ('/path/to/dir/file2.txt', 1, 'file2.txt'),
                    ('/path/to/dir/subdir', 1, 'subdir'),
                    ('/path/to/dir/subdir/file3.txt', 2, 'file3.txt')
                ]
                instructions = {
                    'style': TreeStyle()
                }
            Result:
                /path/to/dir
                ├── file1.txt
                ├── file2.txt
                └── subdir
                    └── file3.txt
        """
        style = instructions.get('style')
        if style:
            return style.write_structure(data)
        return data

#TODO: Move HTMLStyle logic to HTMLFormatter class
class HTMLFormatter(Formatter):
    """
    A concrete implementation of the Formatter class that formats data as HTML.
    """
    def format(self, data: str, instructions=None) -> str:
        """
        Format the data as an HTML string.

        Args:
            data (str): The data to format as HTML.
            instructions (dict): The instructions for formatting the data. Currently not used by the HTML formatter.
        
        Returns:
            str: The data formatted as an HTML string.

        Example:
            Parameters:
                data = [
                    ('/path/to/dir', 0, 'dir'),
                    ('/path/to/dir/file1.txt', 1, 'file1.txt'),
                    ('/path/to/dir/file2.txt', 1, 'file2.txt'),
                    ('/path/to/dir/subdir', 1, 'subdir'),
                    ('/path/to/dir/subdir/file3.txt', 2, 'file3.txt')
                ]
                instructions = {}
            Result:
                <html><body><pre>
                    <ul>
                        <li><a href="dir1/">dir1/</a></li>
                        <ul>
                            <li><a href="file1.txt">file1.txt</a></li>
                            <li><a href="file2.txt">file2.txt</a></li>
                            <li><a href="subdir1/">subdir1/</a></li>
                            <ul>
                                <li><a href="file3.txt">file3.txt</a></li>
                            </ul>
                        </ul>
                    </ul>
                </pre></body></html>
        """
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
