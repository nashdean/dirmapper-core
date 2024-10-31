from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle

class TreeStyle(BaseStyle):
    def write_structure(self, structure: List[Tuple[str, int, str]] | dict, **kwargs) -> str:
        result = []
        if isinstance(structure, list):
            for i, (item_path, level, item) in enumerate(structure):
                indent = '│   ' * level
                is_last = (i == len(structure) - 1 or structure[i + 1][1] < level)
                connector = '└── ' if is_last else '├── '

                if os.path.isdir(item_path):
                    result.append(f"{indent}{connector}{item}/")
                else:
                    result.append(f"{indent}{connector}{item}")
            
            return '\n'.join(result)
        elif isinstance(structure, dict):
            lines = []
            self._write_from_dict(structure, '', True, lines)
            # Calculate the maximum length of lines before comments
            max_length = max(len(line[0]) for line in lines) if lines else 0
            # Format lines with aligned comments
            formatted_lines = []
            for line_content, comment in lines:
                if comment:
                    formatted_lines.append(f"{line_content.ljust(max_length)}  # {comment}")
                else:
                    formatted_lines.append(line_content)
            return '\n'.join(formatted_lines)
    
    def _write_from_dict(self, structure, prefix, is_last, lines, level=0):
        if isinstance(structure, dict):
            items = list(structure.items())
            for idx, (key, value) in enumerate(items):
                is_last_item = idx == len(items) - 1
                connector = '└── ' if is_last_item else '├── '
                indent = self._get_indent(level)
                line = f"{indent}{connector}{key}"
                summary = ''
                if isinstance(value, dict) and 'summary' in value:
                    summary = value['summary']
                # if isinstance(value, dict) or isinstance(value, list):
                #     if not summary:
                #         line += '/'
                lines.append((line, summary))
                if isinstance(value, dict):
                    # Exclude the 'summary' key when recursing
                    child_structure = {k: v for k, v in value.items() if k != 'summary'}
                    self._write_from_dict(child_structure, prefix + key + '/', is_last_item, lines, level + 1)
                elif isinstance(value, list):
                    self._write_from_list(value, prefix + key + '/', is_last_item, lines, level + 1)
        elif isinstance(structure, list):
            self._write_from_list(structure, prefix, is_last, lines, level)
    
    def _write_from_list(self, structure, prefix, is_last, lines, level):
        for idx, item in enumerate(structure):
            is_last_item = idx == len(structure) - 1
            self._write_from_dict(item, prefix, is_last_item, lines, level)
    
    def _get_indent(self, level):
        return '│   ' * level