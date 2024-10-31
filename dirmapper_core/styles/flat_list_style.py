from typing import List, Tuple
from dirmapper_core.styles.base_style import BaseStyle

class FlatListStyle(BaseStyle):
    #TODO: Update this method to work with the template summarizer; see tree_style for details
    def write_structure(self, structure: List[Tuple[str, int, str]], **kwargs) -> str:
        result = [item_path for item_path, _, _ in structure]
        return '\n'.join(result)
