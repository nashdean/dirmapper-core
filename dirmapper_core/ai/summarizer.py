# src/dirmapper/ai/summarizer.py
import copy
import os
from typing import List, Optional, Tuple
from dirmapper_core.formatter.formatter import Formatter
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.styles.tree_style import TreeStyle
from dirmapper_core.utils.logger import logger, log_periodically, stop_logging
from dirmapper_core.writer.template_parser import TemplateParser
from openai import OpenAI, AuthenticationError

import json
import threading

class DirectorySummarizer:
    """
    Class to summarize a directory structure using the OpenAI API or local model.
    """
    def __init__(self, config: dict):
        """
        Initialize the DirectorySummarizer object.

        Args:
            config (dict): Configuration dictionary containing:
                - use_local (bool): Whether to use local summarization
                - api_token (str): OpenAI API token (required if use_local is False)
                - summarize_file_content (bool): Whether to summarize file contents
                - max_file_summary_words (int): Maximum words for file content summaries
        """
        self.is_local = config.get('use_local', True)
        self.client = None
        self.summarize_file_content = config.get('summarize_file_content', False)
        self.max_short_summary_characters = config.get('max_short_summary_characters', 75)
        self.max_file_summary_words = config.get('max_file_summary_words', 50)
        self.file_summarizer = FileSummarizer(config)  # Kept this

        if not self.is_local:
            api_token = config.get("api_token")
            if not api_token:
                raise ValueError("API token is not set. Please set the API token in the preferences.")
            self.client = OpenAI(api_key=api_token)

    def summarize(self, directory_structure: DirectoryStructure) -> str:
        """
        Summarizes the directory structure using the OpenAI API or local model.

        Args:
            directory_structure (DirectoryStructure): The directory structure to summarize.

        Returns:
            str: The directory structure with summaries for each file/folder in the specified format.
        
        Example:
            Parameters:
                directory_structure = DirectoryStructure() # Initialized DirectoryStructure object
            
            Result:
                {
                    "dir1/": {
                        "file1.txt": {
                            "summary": "This file contains the data for the first task.",
                            "short_summary": "This file contains the data for the first task."
                        },
                        "file2.txt": {
                            "summary": "This file contains the data for the second task.",
                            "short_summary": "This file contains the data for the second task."
                        },
                        "subdir1/": {
                            "file3.txt": {
                                "summary": "This file contains the data for the third task.",
                                "short_summary": "This file contains the data for the third task."
                            }
                        }
                    }
        """
        # Convert DirectoryStructure to nested dictionary with __keys__
        # nested_dict = directory_structure.to_nested_dict()
        
        if self.is_local:
            logger.warning('Localized summary functionality under construction. Set preferences to use the api by setting `is_local` to False.')
            return {}

        # Get metadata from first item in directory structure
        meta_data = {
            'root_path': directory_structure.items[0].path if directory_structure.items else ''
        }

        # Summarize the structure
        summarized_structure = self._summarize_api(directory_structure, meta_data)

        # Merge summaries back into the original structure
        if isinstance(summarized_structure, dict):
            directory_structure.merge_nested_dict(summarized_structure)

        return summarized_structure

    def _summarize_api(self, directory_structure: DirectoryStructure, meta_data: dict) -> dict:
        """
        Summarizes the directory structure using the OpenAI API.

        Args:
            directory_structure (dict): The directory structure to summarize.
            meta_data (dict): Metadata about the directory structure.

        Returns:
            dict: The summarized directory structure with summaries in __keys__.content.
        """
        root_path = meta_data.get('root_path', '')
        
        # Preprocess to add content summaries if enabled
        if self.summarize_file_content:
            self._preprocess_structure(directory_structure)
        
        logger.debug("Preprocessed structure:", directory_structure)
        # Create copy for API request without file content
        api_structure = copy.deepcopy(directory_structure)

        # Get summaries from API
        summarized_structure = self._summarize_directory_structure_api(
            api_structure,
            self.max_short_summary_characters     
        )

        return summarized_structure

    def _summarize_local(self, parsed_structure: dict) -> str:
        """
        Summarizes the directory structure using a local model.

        Args:
            parsed_structure (dict): The parsed directory structure to summarize.

        Returns:
            str: The summarized directory structure in the specified structured format.

        Example:
            Parameters:
                parsed_structure = {
                    "dir1/": {
                        "file1.txt": {},
                        "file2.txt": {},
                        "subdir1/": {
                            "file3.txt": {}
                        }
                    }
                }
            Result:
                {
                    "dir1/": {
                        "file1.txt": {
                            "summary": "This file contains the data for the first task."
                        },
                        "file2.txt": {
                            "summary": "This file contains the data for the second task."
                        },
                        "subdir1/": {
                            "file3.txt": {
                                "summary": "This file contains the data for the third task."
                            }
                        }
                    }
                }
        """
        # Preprocess the directory structure to add "summary" keys
        self._preprocess_structure(parsed_structure)
        
        # Summarize the directory structure using the OpenAI API
        summarized_structure = self.summarize_directory_structure_local(parsed_structure, self.format_instruction.get('length'), self.client)

        return summarized_structure

    def _preprocess_structure(self, structure: DirectoryStructure) -> None:
        """
        Preprocesses the directory structure to add content summaries in __keys__.content.
        Modifies the structure in place.

        Args:
            structure (DirectoryStructure): The directory structure to preprocess
        """
        for item in structure.items:
            
            # Summarize content if it's a file
            if item.metadata.get('type') == 'file' and self._should_summarize_file(item.path):
                content = item.content
                if content:
                    logger.debug("Summarizing content for:", item.path)
                    summary = self.file_summarizer.summarize_content(content, self.max_file_summary_words)
                    logger.debug("Summary:", summary)
                    item.summary = summary

    def _should_summarize_file(self, file_path: str) -> bool:
        allowed_extensions = ['.py', '.md', '.txt']
        _, ext = os.path.splitext(file_path)
        return ext.lower() in allowed_extensions

    def _apply_style_and_format(self, summarized_structure: dict) -> str:
        """
        Applies the specified style and format to the summarized directory structure. This method uses the Formatter object to format the structure.

        Args:
            summarized_structure (dict): The summarized directory structure to format.

        Returns:
            str: The formatted directory structure using the specified style and format.
        """
        return self.formatter.format(summarized_structure, self.format_instruction)
    
    def summarize_directory_structure_local(self, directory_structure: str, short_summary_length: int) -> dict:
        """
        Summarizes the directory structure using a local model.

        Args:
            directory_structure (str): The directory structure to summarize.
            short_summary_length (int): The maximum word length for each summary.

        Returns:
            dict: The summarized directory structure in JSON format with summaries for each file/folder.
        """
        # Summarize the directory structure using a local model
        try:
            import transformers
            # Load and run the local model for summarization
            # Your summarization code here
        except ImportError:
            # logger.error("Summarization feature requires additional dependencies. Please run `dirmap install-ai` to set it up.")
            return "Error: Summarization feature requires additional dependencies.  Please run `dirmap install-ai` to set it up."

    def _summarize_directory_structure_api(self, directory_structure: dict, short_summary_length: int) -> dict:
        """
        Summarizes the directory structure using the OpenAI API.

        Args:
            directory_structure (dict): The directory structure to summarize with __keys__.
            short_summary_length (int): The maximum character length for each summary.

        Returns:
            dict: The summarized directory structure in JSON format with summaries in __keys__.content.
        """
        simple_json_structure = directory_structure.to_nested_dict(['type', 'short_summary', 'summary'])
        tree_structure = TreeStyle.write_structure(directory_structure)
        logger.debug("Simple JSON Structure:", json.dumps(simple_json_structure, indent=2))

        messages = [
            {
                "role": "system",
                "content": "You are a directory structure analyzer. Respond only with valid JSON."
            },
            {
                "role": "user", 
                "content": (
                    "Analyze the following directory structure:\n\n"
                    f"{tree_structure}\n\n"
                    "Use the following JSON object that matches the input structure to generate "
                    "`short_summary` fields for each item. Do not modify the structure in any other way. "
                    f"Write each summary in {short_summary_length} characters or less. Here is the formatted JSON:\n\n"
                    f"{json.dumps(simple_json_structure, indent=2)}"
                )
            }
        ]

        logger.info("Sending request to API for summarization")
        stop_logging.clear()
        logging_thread = threading.Thread(
            target=log_periodically, 
            args=("Waiting for response from OpenAI API...", 5)
        )
        logging_thread.start()

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            if not response.choices:
                logger.error("No response from API")
                return directory_structure
                
            # Log the raw response for debugging
            raw_response = response.choices[0].message.content
            logger.debug(f"Raw API Response:\n{raw_response[:500]}...")  # First 500 chars
            
            try:
                summaries = json.loads(raw_response)
                logger.debug("Summaries in _summarize_dir_struct_api:", json.dumps(summaries, indent=2))
                logger.info("Successfully parsed API response")
                return summaries
            except json.JSONDecodeError as e:
                logger.error(f"JSON Parse Error at position {e.pos}: {raw_response[max(0, e.pos-50):e.pos+50]}")
                return directory_structure
                
        except Exception as e:
            logger.error(f"API Error: {str(e)}")
            return directory_structure
            
        finally:
            stop_logging.set()
            logging_thread.join()

class FileSummarizer:
    """
    Class to summarize a file's content using the OpenAI API or a local model.
    """
    def __init__(self, config: dict):
        """
        Initialize the FileSummarizer object.

        Args:
            config (dict): The config for the summarizer.
        """
        self.is_local = config.get("use_local", False)
        self.client = None
        if not self.is_local:
            api_token = config.get("api_token")
            if not api_token:
                raise ValueError("API token is not set. Please set the API token in the preferences.")
            self.client = OpenAI(api_key=api_token)

    def summarize_content(self, content: str, max_words: int = 100) -> str:
        """
        Summarizes the content using the OpenAI API or local model.

        Args:
            content (str): The content to summarize.

        Returns:
            str: The summarized content.
        """
        if self.is_local:
            logger.warning('Local summarization is not implemented yet.')
            return "Local summarization is not implemented yet."
        else:
            # Check content size
            max_content_length = 5000  # Adjust based on API limits
            if len(content) > max_content_length:
                logger.info(f"File is large; summarizing in chunks.")
                return self._summarize_large_content(content, max_words)
            else:
                return self._summarize_api(content, max_words)

    def summarize_file(self, file_path: str, max_words: int = 100) -> str:
        """
        Summarizes the content of a file.

        Args:
            file_path (str): The path to the file to summarize.
            max_words (int): The maximum number of words for the summary.

        Returns:
            str: The markdown summary of the file.
        """
        if not os.path.isfile(file_path):
            logger.error(f"File not found: {file_path}")
            return ""

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

        if self.is_local:
            logger.warning('Local summarization is not implemented yet.')
            return "Local summarization is not implemented yet."
        else:
            # Check content size
            max_content_length = 5000  # Adjust based on API limits
            if len(content) > max_content_length:
                logger.info(f"File is large; summarizing in chunks.")
                return self._summarize_large_content(content, max_words)
            else:
                return self._summarize_api(content, max_words)

    def _summarize_large_content(self, content: str, max_words: int) -> str:
        """
        Summarizes large content by splitting it into chunks.

        Args:
            content (str): The content to summarize.
            max_words (int): The maximum number of words for the summary.

        Returns:
            str: The combined summary of all chunks.
        """
        chunk_size = 4000  # Adjust based on API limits
        chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
        summaries = []

        for idx, chunk in enumerate(chunks):
            logger.info(f"Summarizing chunk {idx + 1}/{len(chunks)}")
            summary = self._summarize_api(chunk, max_words)
            summaries.append(summary)

        # Combine summaries
        combined_summary = "\n".join(summaries)
        # Optionally, summarize the combined summary if it's still too long
        if len(combined_summary) > chunk_size:
            logger.info("Summarizing the combined summary.")
            combined_summary = self._summarize_api(combined_summary, max_words)

        return combined_summary
    
    def _summarize_api(self, content: str, max_words: int) -> str:
        """
        Summarizes the content using the OpenAI API.

        Args:
            content (str): The content to summarize.
            max_words (int): The maximum number of words for the summary.

        Returns:
            str: The markdown summary of the content.
        """
        max_tokens = 2048
        temperature = 0.5
        model = "gpt-4o-mini"

        # Prepare the prompt
        messages = [
            {"role": "system", "content": "You are a helpful assistant that summarizes content into markdown format."},
            {"role": "user", "content": f"Please provide a concise summary (max {max_words} words) of the following content in markdown format removing the wrapper"
                f" '```markdown' and '```' block. Here is the content :\n\n{content}"}
        ]

        logger.info(f"Sending request to OpenAI API for summarization.")

        stop_logging.clear()
        logging_thread = threading.Thread(target=log_periodically, args=("Waiting for response from OpenAI API...", 5))
        logging_thread.start()

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            if not response or not response.choices:
                logger.error("Empty or invalid response from API")
                return ""

            summary = response.choices[0].message.content.strip()
            # summary = summary.replace("```markdown\n", "").replace("```", "")
            return summary
        except AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error during API call: {e}")
            return ""
        finally:
            stop_logging.set()
            logging_thread.join()