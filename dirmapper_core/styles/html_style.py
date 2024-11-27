from typing import List, Tuple
import os
from dirmapper_core.styles.base_style import BaseStyle

class HTMLStyle(BaseStyle):
    """
    HTMLStyle class for generating a directory structure in an HTML format.
    """
    #TODO: Update this method to work with the template summarizer; see tree_style for context
    def write_structure(structure: List[Tuple[str, int, str]], **kwargs) -> str:
        """
        Write the directory structure in an HTML format.

        Args:
            structure (list): The directory structure to write. The structure should be a list of tuples. Each tuple should contain the path, level, and item name.
        
        Returns:
            str: The directory structure in an HTML format.
        
        Example:
            Parameters:
                structure = [
                    ('dir1/', 0, 'dir1'),
                    ('dir1/file1.txt', 1, 'file1.txt'),
                    ('dir1/file2.txt', 1, 'file2.txt'),
                    ('dir1/subdir1/', 1, 'subdir1'),
                    ('dir1/subdir1/file3.txt', 2, 'file3.txt')
                ]
            Result:
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
        """
        result = ['<ul>']
        previous_level = -1

        for item_path, level, item in structure:
            if level > previous_level:
                result.append('<ul>')
            elif level < previous_level:
                result.append('</ul>' * (previous_level - level))

            relative_path = os.path.relpath(item_path, start=structure[0][0])
            if os.path.isdir(item_path):
                result.append(f'<li><a href="{relative_path}">{item}/</a></li>')
            else:
                result.append(f'<li><a href="{relative_path}">{item}</a></li>')

            previous_level = level

        result.append('</ul>' * (previous_level + 1))
        return '\n'.join(result)
