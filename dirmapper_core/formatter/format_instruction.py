# src/dirmapper/formatter/format_instruction.py
from abc import ABC, abstractmethod

class FormatInstruction(ABC):
    """
    Abstract class for format instructions.
    """
    summary_word_length = 0
    @abstractmethod
    def get_instruction(self, output_type) -> str:
        """
        Get the format instruction for the specified output type.
        """
        pass

class MinimalistFormatInstruction(FormatInstruction):
    """
    A concrete implementation of the FormatInstruction class that provides format instructions for a minimalist project structure.
    """
    allowed_output_types = ['summary', 'structure']
    summary_word_length = 5

    def get_instruction(self, output_type) -> str:
        """
        Get the format instruction for the minimalist format.

        Args:
            output_type (str): The type of output to generate the format instruction for.
        
        Returns:
            str: The format instruction for the specified output type.
        """
        if output_type not in self.allowed_output_types:
            raise ValueError(f"Invalid output type: {output_type}")
        
        return (
            f"Format the {output_type} as follows:\n"
            ".git/                          # Git metadata\n"
            ".github/                       # GitHub CI configuration\n"
            "\tworkflows/                   # GitHub Actions workflows\n"
            ".gitignore                     # Files to ignore in Git\n"
            "LICENSE                        # License file\n"
            "Makefile                       # Automation commands\n"
            "pyproject.toml                 # Python project config\n"
            "README.md                      # Project overview\n"
            "requirements.txt               # Python dependencies\n"
            "src/                           # Source code\n"
            "tests/                         # Unit tests"
        )

# Add other format instructions similarly