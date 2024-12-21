from typing import List
from dirmapper_core.models.directory_structure import DirectoryStructure

class DirectoryPaginator:
    """
    Class to paginate a directory structure into smaller chunks.
    """
    def __init__(self, max_items_per_page: int = 20):
        """
        Initialize the DirectoryPaginator object.

        Args:
            max_items_per_page (int): Maximum number of items per page.
        """
        self.max_items_per_page = max_items_per_page

    def paginate(self, directory_structure: DirectoryStructure) -> List[DirectoryStructure]:
        """
        Paginate the directory structure into smaller chunks.

        Args:
            directory_structure (DirectoryStructure): The directory structure to paginate.

        Returns:
            List[DirectoryStructure]: List of paginated directory structures.
        """
        paginated_structures = []
        current_structure = DirectoryStructure()
        for idx, item in enumerate(directory_structure.items):
            if idx > 0 and idx % self.max_items_per_page == 0:
                paginated_structures.append(current_structure)
                current_structure = DirectoryStructure()
            current_structure.add_item(item)
        if current_structure.items:
            paginated_structures.append(current_structure)
        return paginated_structures
