from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle

class ListStyle(BaseStyle):
    #TODO: Update this method to work with the template summarizer; see tree_style for details
    def write_structure(self, structure: List[Tuple[str, int, str]], **kwargs) -> str:
        result = []
        for item_path, level, item in structure:
            indent = '    ' * level
            if os.path.isdir(item_path):
                result.append(f"{indent}- {item}/")
            else:
                result.append(f"{indent}- {item}")
        return '\n'.join(result)
