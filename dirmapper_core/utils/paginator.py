from typing import List, Tuple
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.utils.logger import logger

class DirectoryPaginator:
    """
    Class to paginate a directory structure into smaller chunks.
    """
    def __init__(self, max_items_per_page: int = 20, max_tokens: int = 4000):
        """
        Initialize the DirectoryPaginator object.

        Args:
            max_items_per_page (int): Maximum number of items per page.
            max_tokens (int): Maximum number of tokens allowed per API request.
        """
        self.max_items_per_page = max_items_per_page
        self.max_tokens = max_tokens

    def should_paginate(self, directory_structure: DirectoryStructure) -> Tuple[bool, int]:
        """
        Determine if the directory structure should be paginated.

        Args:
            directory_structure (DirectoryStructure): The directory structure to check.

        Returns:
            Tuple[bool, int]: (should_paginate, estimated_tokens)
        """
        estimated_tokens = self._estimate_tokens(directory_structure)
        should_paginate = (
            len(directory_structure.items) > self.max_items_per_page or 
            estimated_tokens > self.max_tokens
        )
        
        if should_paginate:
            logger.info(f"Directory structure requires pagination. Items: {len(directory_structure.items)}, "
                       f"Estimated tokens: {estimated_tokens}")
        
        return should_paginate, estimated_tokens

    def _estimate_tokens(self, directory_structure: DirectoryStructure) -> int:
        """
        Estimate the number of tokens in the directory structure.
        Rough estimation: 1 token ≈ 4 characters
        
        Args:
            directory_structure (DirectoryStructure): The directory structure to estimate.
            
        Returns:
            int: Estimated number of tokens
        """
        total_chars = 0
        for item in directory_structure.items:
            # Count path characters
            total_chars += len(item.path)
            
            # Count metadata characters
            if item.metadata:
                total_chars += len(str(item.metadata))
            
            # Count summary characters if they exist
            if hasattr(item, 'summary'):
                total_chars += len(item.summary or '')
            if hasattr(item, 'short_summary'):
                total_chars += len(item.short_summary or '')

        # Rough estimation: 1 token ≈ 4 characters
        estimated_tokens = total_chars // 4
        return estimated_tokens

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
