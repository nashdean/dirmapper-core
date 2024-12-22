import string
import math
from typing import Optional
from dirmapper_core.utils.logger import logger
import re

class TextAnalyzer:
    """
    Utility class for analyzing text content characteristics.
    """
    def __init__(self, entropy_threshold: float = 5.0):
        """
        Initialize TextAnalyzer with configurable threshold.

        Args:
            entropy_threshold (float): Threshold for determining high entropy content
        """
        self.entropy_threshold = entropy_threshold
        # Common text file patterns
        self.text_patterns = [
            r'^#!.*python',  # Shebang for Python
            r'^#!.*node',    # Shebang for Node.js
            r'^#!.*bash',    # Shebang for Bash
            r'^#\s*-\*-\s*coding[:=]\s*(utf|ascii|latin|cp\d+)',  # Python encoding
            r'package\s+[\w\.]+;',  # Java package declaration
            r'import\s+[\w\.]+;',   # Java/JavaScript imports
            r'from\s+[\w\.]+\s+import', # Python imports
            r'def\s+\w+\s*\(',      # Python function definition
            r'function\s+\w+\s*\(', # JavaScript function
            r'class\s+\w+[\s{]',    # Class definitions
            r'^\s*<\?xml',          # XML declaration
            r'^\s*<!DOCTYPE',       # DOCTYPE declaration
            r'^\s*{',               # JSON start
            r'^\s*[\'"]use strict', # JavaScript strict mode
            r'---\s*$',             # YAML document start
            r'^\s*//.*$',           # Single-line comments
            r'^\s*/\*',             # Multi-line comments
            r'^\s*#.*$',            # Hash comments
            r'^\s*"""',             # Python docstring
            r'^\s*\'\'\'',          # Python docstring alternative
        ]

    def is_high_entropy(self, content: str) -> bool:
        """
        Checks if the content has high entropy, indicating randomness.
        Uses multiple heuristics to determine if content is likely binary.

        Args:
            content (str): The content to check.

        Returns:
            bool: True if the content appears to be binary, False otherwise.
        """
        # Check for common text file patterns first
        if self._has_text_file_patterns(content):
            return False

        # Sample the content if it's too long
        sample = content[:4000] if len(content) > 4000 else content
        
        # Calculate entropy on the sample
        entropy = self._calculate_entropy(sample)
        
        # Check character distribution
        printable_ratio = self._get_printable_ratio(sample)
        
        # Content is considered high entropy if:
        # 1. Entropy is above threshold AND
        # 2. Printable character ratio is below 0.95
        is_binary = entropy > self.entropy_threshold and printable_ratio < 0.95
        
        logger.info(f"Entropy: {entropy:.2f}, Printable ratio: {printable_ratio:.2f}, "
                    f"Is binary: {is_binary}")
        
        return is_binary

    def _calculate_entropy(self, content: str) -> float:
        """
        Calculates the entropy of the content using normalized character frequencies.

        Args:
            content (str): The content to calculate entropy for.

        Returns:
            float: The entropy of the content.
        """
        if not content:
            return 0.0
        
        # Count character frequencies
        frequency = {}
        content_length = len(content)
        
        # Group similar characters to reduce entropy variation

        for char in content:
            if char.isspace():
                char = ' '  # Treat all whitespace as space
            elif char.isalpha():
                char = 'a'  # Treat all letters as 'a'
            elif char.isdigit():
                char = '0'  # Treat all digits as '0'
            
            frequency[char] = frequency.get(char, 0) + 1

        # Calculate entropy using normalized frequencies
        entropy = 0
        for count in frequency.values():
            p = count / content_length
            entropy -= p * math.log2(p)
        
        return entropy

    def _get_printable_ratio(self, content: str) -> float:
        """
        Calculate the ratio of printable characters to total characters.

        Args:
            content (str): The content to analyze.

        Returns:
            float: Ratio of printable characters (0.0 to 1.0)
        """
        if not content:
            return 1.0
        
        printable_chars = sum(1 for c in content if c in string.printable)
        return printable_chars / len(content)

    def _has_text_file_patterns(self, content: str) -> bool:
        """
        Check if the content contains common text file patterns.

        Args:
            content (str): The content to check.

        Returns:
            bool: True if content matches text file patterns.
        """
        # Take first few lines for pattern matching
        first_lines = '\n'.join(content.splitlines()[:10])
        
        return any(re.search(pattern, first_lines, re.MULTILINE) 
                  for pattern in self.text_patterns)

    def has_non_printable_chars(self, content: str) -> bool:
        """
        Checks if the content contains non-printable characters.

        Args:
            content (str): The content to check.

        Returns:
            bool: True if the content contains non-printable characters, False otherwise.
        """
        if not content:
            return False
            
        # Allow common whitespace characters
        allowed_chars = set(string.printable)
        allowed_chars.update('\n', '\r', '\t')
        
        # Check only a sample of the content for performance
        sample = content[:4000] if len(content) > 4000 else content
        non_printable = set(char for char in sample if char not in allowed_chars)
        
        # Allow up to 1% non-printable characters
        non_printable_ratio = len(non_printable) / len(sample)
        return non_printable_ratio > 0.01

    def is_binary_content(self, content: Optional[str]) -> bool:
        """
        Determines if content appears to be binary based on multiple heuristics.

        Args:
            content (Optional[str]): The content to analyze.

        Returns:
            bool: True if the content appears to be binary, False otherwise.
        """
        if not content:
            return False
        
        # Check for known text file patterns first
        if self._has_text_file_patterns(content):
            return False
            
        return (self.is_high_entropy(content) and 
                self.has_non_printable_chars(content))
