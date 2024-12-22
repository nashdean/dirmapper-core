from typing import List, Tuple, Dict
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.utils.logger import logger
from collections import defaultdict

class DirectoryPaginator:
    """
    Class to paginate a directory structure into smaller chunks.
    Supports both item-count based and level-based pagination.
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

    def paginate(self, directory_structure: DirectoryStructure, by_level: bool = False) -> List[DirectoryStructure]:
        """
        Paginate the directory structure into smaller chunks.

        Args:
            directory_structure (DirectoryStructure): The directory structure to paginate.
            by_level (bool): If True, paginate by directory levels instead of item count.

        Returns:
            List[DirectoryStructure]: List of paginated directory structures.
        """
        if by_level:
            return self.paginate_by_level(directory_structure)
        
        # Original item-count based pagination
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

    def paginate_by_level(self, directory_structure: DirectoryStructure) -> List[DirectoryStructure]:
        """
        Paginate the directory structure by directory levels.
        Each page contains a complete level of the directory structure.

        Args:
            directory_structure (DirectoryStructure): The directory structure to paginate.

        Returns:
            List[DirectoryStructure]: List of paginated directory structures, one per level.
        """
        # Group items by level
        level_groups = defaultdict(list)
        for item in directory_structure.items:
            level_groups[item.level].append(item)

        # Create a DirectoryStructure for each level
        paginated_structures = []
        for level in sorted(level_groups.keys()):
            level_structure = DirectoryStructure()
            
            # Add parent directories to provide context
            parent_dirs = self._get_parent_directories(level_groups[level], directory_structure)
            for parent in parent_dirs:
                level_structure.add_item(parent)
            
            # Add current level items
            for item in level_groups[level]:
                level_structure.add_item(item)
            
            paginated_structures.append(level_structure)
            logger.debug(f"Created page for level {level} with {len(level_structure.items)} items")

        return paginated_structures

    def _get_parent_directories(self, items: List[DirectoryItem], original_structure: DirectoryStructure) -> List[DirectoryItem]:
        """
        Get all parent directories for a list of items.

        Args:
            items (List[DirectoryItem]): List of items to get parents for.
            original_structure (DirectoryStructure): The original directory structure.

        Returns:
            List[DirectoryItem]: List of parent directory items.
        """
        parent_paths = set()
        for item in items:
            path_parts = item.path.split('/')
            # Add all parent paths
            for i in range(1, len(path_parts)):
                parent_path = '/'.join(path_parts[:i])
                if parent_path:
                    parent_paths.add(parent_path)

        # Get parent DirectoryItems from original structure
        parent_items = []
        for path in parent_paths:
            parent = original_structure.get_item(path)
            if parent and parent not in parent_items:
                parent_items.append(parent)

        return sorted(parent_items, key=lambda x: len(x.path.split('/')))
