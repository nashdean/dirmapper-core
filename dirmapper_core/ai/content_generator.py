from typing import List
from dirmapper_core.ai.summarizer import DirectorySummarizer
from openai import OpenAI
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.utils.logger import logger

class ContentGenerator:
    """
    Class to generate content for files based on the directory structure and its items.
    """
    def __init__(self, api_key: str):
        """
        Initialize the ContentGenerator object.

        Args:
            api_key (str): OpenAI API key.
        """
        self.client = OpenAI(api_key=api_key)

    def generate_file_content(self, path: str, directory_structure: DirectoryStructure) -> str:
        """
        Generate content for the specified file based on the directory structure and its items.

        Args:
            path (str): The path of the file to generate content for.
            directory_structure (DirectoryStructure): The directory structure of the project.

        Returns:
            str: The generated content for the file.
        """
        prompt = self._build_prompt(path, directory_structure)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an assistant that generates file content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            generated_content = response['choices'][0]['message']['content'].strip()
            return generated_content
        except Exception as e:
            logger.error(f"Error generating content for {path}: {str(e)}")
            return ""

    def _build_prompt(self, path: str, directory_structure: DirectoryStructure) -> str:
        """
        Build the prompt for the OpenAI API based on the directory structure and its items.

        Args:
            path (str): The path of the file to generate content for.
            directory_structure (DirectoryStructure): The directory structure of the project.

        Returns:
            str: The prompt for the OpenAI API.
        """
        
        if not directory_structure.description:
            DirectorySummarizer().summarize_project(directory_structure)

        project_summary = f"This project is about: {directory_structure.description}\n"
        directory_context = "The project has the following structure:\n"
        
        # Create a hierarchical view of items
        for item in directory_structure.items:
            indent = '    ' * item.level
            directory_context += f"{indent}{item.name}\n"

        prompt = (
            f"{project_summary}\n\n"
            f"{directory_context}\n\n"
            f"Generate content for the file at '{path}'."
        )
        return prompt
