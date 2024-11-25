# src/dirmapper/ai/summarizer.py
import copy
import os
from typing import Optional
from dirmapper_core.formatter.formatter import Formatter
from dirmapper_core.utils.logger import logger, log_periodically, stop_logging
from dirmapper_core.writer.template_parser import TemplateParser
from openai import OpenAI, AuthenticationError

import json
import threading

class DirectorySummarizer:
    """
    Class to summarize a directory structure using the OpenAI API or local model.
    """
    def __init__(self, formatter: Formatter, format_instruction: dict, config: dict):
        """
        Initialize the DirectorySummarizer object.

        Args:
            formatter (Formatter): The Formatter object to format the summarized directory structure. Valid output formats are "json" and "plaintext". See Formatter class for more details.
            format_instruction (dict): The format instruction for the summarization. Expected keys are "length", "summarize_file_content", and "file_summary_word_length".
            config (dict): The config for the summarizer. Expected keys are "use_local" and "api_token".
        """
        self.is_local = config.get("use_local")
        self.formatter = formatter
        self.format_instruction = format_instruction
        self.client = None
        self.summarize_file_content = format_instruction.get('summarize_file_content', False)
        self.file_summarizer = FileSummarizer(config)
        self.max_file_summary_words = format_instruction.get('file_summary_word_length', 100)
        if not self.is_local:
            api_token = config.get("api_token")
            if not api_token:
                raise ValueError("API token is not set. Please set the API token in the preferences.")
            self.client = OpenAI(api_key=api_token)

    def summarize(self, directory_structure: str) -> str:
        """
        Summarizes the directory structure using the OpenAI API or local model.

        Args:
            directory_structure (str): The directory structure to summarize.

        Returns:
            str: The directory structure with summaries for each file/folder in the specified structured format.
        
        Example:
            Parameters:
                directory_structure = {
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

        if isinstance(directory_structure, dict):
            # Already a dict, assume it's the parsed directory structure
            parsed_structure = directory_structure
        elif isinstance(directory_structure, str):
            # Try to parse as JSON
            try:
                directory_dict = json.loads(directory_structure)
                parsed_structure = directory_dict
            except json.JSONDecodeError:
                # Not JSON, assume it's a tree-like directory string
                parser = TemplateParser()
                parsed_structure = parser.parse_from_directory_structure(directory_structure)
        else:
            raise ValueError("directory_structure must be a str or dict")
        
        # Extract the 'template' part if present
        if 'template' in parsed_structure:
            template_structure = parsed_structure['template']
            meta_data = parsed_structure.get('meta', {})
        else:
            # No 'template' key, assume the whole structure is the directory structure
            template_structure = parsed_structure
            meta_data = {}

        if self.is_local:
            logger.warning('Localized summary functionality under construction. Set preferences to use the api by setting `is_local` to False.')
            return "Localized summary functionality coming soon..."
        summarized_structure = self._summarize_api(template_structure, meta_data)

        # Reconstruct the full structure if 'meta' was present
        if 'template' in parsed_structure:
            summarized_full_structure = {
                'meta': meta_data,
                'template': summarized_structure
            }
        else:
            summarized_full_structure = summarized_structure
        # Now format the summarized_full_structure
        formatted_output = self._apply_style_and_format(summarized_full_structure)
        return formatted_output

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
        summarized_structure = self._apply_style_and_format(summarized_structure)

        return summarized_structure

    def _summarize_api(self, directory_structure: dict, meta_data: dict) -> dict:
        """
        Summarizes the directory structure using the OpenAI API.

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
        root_path = meta_data.get('root_path','')
        # Preprocess the directory structure to add "summary" keys
        self._preprocess_structure(directory_structure, root_path=root_path)
        
        # Prepare the directory structure for sending to the API
        # Remove 'rel_path' keys before sending
        directory_structure_for_api = copy.deepcopy(directory_structure)
        self._remove_rel_path(directory_structure_for_api)

        # Summarize the directory structure using the OpenAI API
        summarized_structure = self.summarize_directory_structure_api(directory_structure, self.format_instruction.get('length'))
        
        # Restore 'rel_path' keys after receiving the response
        self._restore_rel_path(original_structure=directory_structure, new_structure=summarized_structure)
        # print()
        # print(summarized_structure)
        # print()

        return summarized_structure

    def _preprocess_structure(self, parsed_structure: dict, current_path: str = "", root_path: Optional[str] = None):
        """
        Preprocesses the directory structure to add "summary" keys. This is a recursive function that modifies the input structure in place.

        Args:
            parsed_structure (dict): The parsed directory structure to preprocess.
            current_path (str): The current file system path.
            root_path (str): The root path of the directory structure on the file system.
        """
        for key, value in parsed_structure.items():
            # Remove trailing slash for directories
            name = key.rstrip('/')
            # Build the relative path from the root
            rel_path = os.path.join(current_path, name)

            # Add 'rel_path' key to value
            value['rel_path'] = rel_path

            if key.endswith('/'):
                # It's a directory
                value['summary'] = ""
                # Recurse into the directory
                self._preprocess_structure(value, current_path=rel_path, root_path=root_path)
            else:
                # It's a file
                value['summary'] = ""
                # Only attempt to summarize file content if we have a valid root_path and the file exists
                if root_path:
                    file_full_path = os.path.join(root_path, rel_path)
                    if os.path.exists(file_full_path):
                        # Skip certain files and check if file content should be summarized
                        if self.summarize_file_content and self._should_summarize_file(file_full_path):
                            summary = self.file_summarizer.summarize_file(file_full_path, self.max_file_summary_words)
                            value['summary'] = summary
                    else:
                        logger.warning(f"File not found: {file_full_path}, skipping content summarization")
                else:
                    logger.warning(f"No root path provided, skipping content summarization for file: {rel_path}")

    
    def _remove_rel_path(self, directory_structure: dict):
        for key, value in directory_structure.items():
            value.pop('rel_path', None)
            if isinstance(value, dict):
                self._remove_rel_path(value)

    def _restore_rel_path(self, original_structure: dict, new_structure: dict):
        for key, value in original_structure.items():
            summarized_value = new_structure.get(key, {})
            rel_path = value.get('rel_path')
            if rel_path:
                summarized_value['rel_path'] = rel_path
            if isinstance(value, dict) and isinstance(summarized_value, dict):
                self._restore_rel_path(value, summarized_value)

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
    
    def summarize_directory_structure_local(self, directory_structure: str, summary_word_length: int) -> dict:
        """
        Summarizes the directory structure using a local model.

        Args:
            directory_structure (str): The directory structure to summarize.
            summary_word_length (int): The maximum word length for each summary.

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

    def summarize_directory_structure_api(self, directory_structure: dict, summary_word_length: int) -> dict:
        """
        Summarizes the directory structure using the OpenAI API.

        Args:
            directory_structure (dict): The directory structure to summarize.
            summary_word_length (int): The maximum word length for each summary.

        Returns:
            dict: The summarized directory structure in JSON format with summaries for each file/folder.
        """
        max_tokens = 2048  # Increase the max tokens limit
        temperature = 0.5
        model = "gpt-4o-mini"

        #TODO: Need to update the second message to match the new directory structure template format where files are nested within directories and directories are dictionaries with a '/' suffix
        messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that summarizes directory structures."
        },
        {
            "role": "user",
            "content": (
                "Analyze the following directory structure represented in JSON format. "
                "In this format:\n"
                "- Directories are represented as dictionary keys ending with a '/'. "
                "Their contents are nested within these dictionaries.\n"
                "- Files are represented as dictionary keys without a trailing '/'. "
                "Their values are dictionaries that may contain a 'summary' key.\n"
                "Your task is to add a 'summary' key to each file's dictionary, summarizing the purpose of the file "
                "in no more than {summary_word_length} words. Do not modify directory keys or add summaries to directories.\n"
                "Return only the updated JSON object with the summaries added. Do not include any explanations or extra text.\n"
                "Ensure that the output is valid JSON.\n"
                "Here is the directory structure:\n```json\n{directory_structure}\n```"
            ).format(
                summary_word_length=summary_word_length,
                directory_structure=json.dumps(directory_structure, indent=4)
            )
        }
    ]
        logger.info(f"Sending request to API for summarization with model: {model}")

        stop_logging.clear()
        logging_thread = threading.Thread(target=log_periodically, args=("Waiting for response from OpenAI API...", 5))
        logging_thread.start()

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={ "type": "json_object" }
            )
            if not response or not response.choices:
                logger.error("Empty or invalid response from API")
                return directory_structure

            summaries = json.loads(response.choices[0].message.content)
        except AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return directory_structure
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return directory_structure
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return directory_structure
        finally:
            stop_logging.set()
            logging_thread.join()

        return summaries

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
            {"role": "user", "content": f"Please provide a concise summary (max {max_words} words) of the following content in markdown format:\n\n{content}"}
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