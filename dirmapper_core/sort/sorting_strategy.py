from abc import ABC, abstractmethod
from typing import Tuple
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

def parse_sort_argument(sort_arg: str) -> Tuple[str, bool]:
    """
    Parses the sort argument to determine the sorting strategy and case sensitivity.

    Args:
        sort_arg (str): The sort argument in the format 'asc', 'asc:case', 'desc', or 'desc:case'.

    Returns:
        tuple: A tuple containing the sort order and case sensitivity flag.
    """
    if sort_arg is None:
        return None, False
    
    parts = sort_arg.split(':')
    sort_order = parts[0]
    case_sensitive = True if len(parts) > 1 and parts[1] == 'case' else False
    return sort_order, case_sensitive
