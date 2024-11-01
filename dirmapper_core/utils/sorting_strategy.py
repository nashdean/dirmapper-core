from abc import ABC, abstractmethod
from dirmapper_core.utils.logger import logger

class SortingStrategy(ABC):
    """
    Abstract class for sorting strategies.
    """
    @abstractmethod
    def sort(self, items, case_sensitive: bool = True):
        pass

class NoSortStrategy(SortingStrategy):
    """
    Class for no sorting strategy.
    """
    def __init__(self):
        """
        Initialize the NoSortStrategy object.
        """
        logger.info('No sorting strategy set.')

    def sort(self, items: list) -> list:
        """
        Sort the items using the no sorting strategy.

        Args:
            items (list): The items to sort.
        
        Returns:
            list: The sorted items.
        """
        return items

class AscendingSortStrategy(SortingStrategy):
    """
    Class for ascending sorting strategy.
    """
    def __init__(self, case_sensitive: bool = True):
        """
        Initialize the AscendingSortStrategy object.

        Args:
            case_sensitive (bool): Whether to sort case sensitive or not.
        """
        self.case_sensitive = case_sensitive
        logger.info(f'Sorting strategy set to Ascending order. Sorting is {"case sensitive" if self.case_sensitive else "not case sensitive"}.')

    def sort(self, items):
        """
        Sort the items using the ascending sorting strategy.

        Args:
            items (list): The items to sort.

        Returns:
            list: The sorted items in ascending order.
        """
        if not self.case_sensitive:
            return sorted(items, key=str.lower)
        return sorted(items)

class DescendingSortStrategy(SortingStrategy):
    """
    Class for descending sorting strategy.
    """
    def __init__(self, case_sensitive: bool = True):
        """
        Initialize the DescendingSortStrategy object.

        Args:
            case_sensitive (bool): Whether to sort case sensitive or not.
        """
        self.case_sensitive = case_sensitive
        logger.info(f'Sorting strategy set to Descending order. Case sensitivity is {"case sensitive" if self.case_sensitive else "not case sensitive"}.')

    def sort(self, items):
        """
        Sort the items using the descending sorting strategy.

        Args:
            items (list): The items to sort.
        
        Returns:
            list: The sorted items in descending order.
        """
        if not self.case_sensitive:
            return sorted(items, key=str.lower, reverse=True)
        return sorted(items, reverse=True)
