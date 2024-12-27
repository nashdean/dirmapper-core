import json
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.formatter.base_formatter import BaseFormatter

class PlainTextFormatter(BaseFormatter):
    """
    Formats directory structure as plain text using the provided style.
    """
    def format(self, data: DirectoryStructure, instructions: dict = None) -> str:
        if not instructions or 'style' not in instructions:
            raise ValueError("Style must be provided in instructions")
        
        style = instructions.get('style')
        style_instructions = {k: v for k, v in instructions.items() if k != 'style'}
        return style.write_structure(data, **style_instructions)

class HTMLFormatter(BaseFormatter):
    """
    Formats directory structure as HTML.
    """
    def format(self, data: DirectoryStructure, instructions: dict = None) -> str:
        if not instructions or 'style' not in instructions:
            raise ValueError("Style must be provided in instructions")
            
        style = instructions.get('style')
        html_data = style.write_structure(data)
        return f"<html><body><pre>{html_data}</pre></body></html>"

class JSONFormatter(BaseFormatter):
    """
    Formats directory structure as JSON.
    """
    def format(self, data: DirectoryStructure, instructions: dict = None) -> str:
        if not instructions or 'style' not in instructions:
            raise ValueError("Style must be provided in instructions")
            
        style = instructions.get('style')
        return json.dumps(style.write_structure(data, **(instructions or {})), indent=4)

class MarkdownFormatter(BaseFormatter):
    """
    Formats directory structure as Markdown.
    """
    def format(self, data: DirectoryStructure, instructions: dict = None) -> str:
        if not instructions or 'style' not in instructions:
            raise ValueError("Style must be provided in instructions")
            
        style = instructions.get('style')
        return style.write_structure(data)
