# src/dirmapper/ai/summarizer.py
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
    def __init__(self, formatter: Formatter, format_instruction: dict, preferences: dict):
        """
        Initialize the DirectorySummarizer object.

        Args:
            formatter (Formatter): The Formatter object to format the summarized directory structure.
            format_instruction (dict): The format instruction for the summarization.
            preferences (dict): The preferences for the summarizer.
        """
        self.is_local = preferences.get("use_local")
        self.formatter = formatter
        self.format_instruction = format_instruction
        self.client = None
        if not self.is_local:
            api_token = preferences.get("api_token")
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
                    "dir1": {
                        "file1.txt": {},
                        "file2.txt": {},
                        "subdir1": {
                            "file3.txt": {}
                        }
                    }
                }
            Result:
                {
                    "dir1": {
                        "file1.txt": {
                            "summary": "This file contains the data for the first task."
                        },
                        "file2.txt": {
                            "summary": "This file contains the data for the second task."
                        },
                        "subdir1": {
                            "file3.txt": {
                                "summary": "This file contains the data for the third task."
                            }
                        }
                    }
                }
        """

        parser = TemplateParser()
        parsed_structure = parser.parse_directory_structure(directory_structure)['template']

        if self.is_local:
            logger.warning('Localized summary functionality under construction. Set preferences to use the api by setting `is_local` to False.')
            return "Localized summary functionality coming soon..."
        return self._summarize_api(parsed_structure)

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
                    "dir1": {
                        "file1.txt": {},
                        "file2.txt": {},
                        "subdir1": {
                            "file3.txt": {}
                        }
                    }
                }
            Result:
                {
                    "dir1": {
                        "file1.txt": {
                            "summary": "This file contains the data for the first task."
                        },
                        "file2.txt": {
                            "summary": "This file contains the data for the second task."
                        },
                        "subdir1": {
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
        summarized_structure = self.summarize_directory_structure_local(parsed_structure, self.format_instruction.summary_word_length, self.client)
        summarized_structure = self._apply_style_and_format(summarized_structure)

        return summarized_structure

    def _summarize_api(self, parsed_structure: dict) -> str:
        """
        Summarizes the directory structure using the OpenAI API.

        Args:
            parsed_structure (dict): The parsed directory structure to summarize.

        Returns:
            str: The summarized directory structure in the specified structured format.

        Example:
            Parameters:
                parsed_structure = {
                    "dir1": {
                        "file1.txt": {},
                        "file2.txt": {},
                        "subdir1": {
                            "file3.txt": {}
                        }
                    }
                }
            Result:
                {
                    "dir1": {
                        "file1.txt": {
                            "summary": "This file contains the data for the first task."
                        },
                        "file2.txt": {
                            "summary": "This file contains the data for the second task."
                        },
                        "subdir1": {
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
        summarized_structure = self.summarize_directory_structure_api(parsed_structure, self.format_instruction.get('length'), self.client)
        # print()
        # print(summarized_structure)
        # print()
        summarized_structure = self._apply_style_and_format(summarized_structure)

        return summarized_structure

    def _preprocess_structure(self, parsed_structure: dict):
        """
        Preprocesses the directory structure to add "summary" keys. This is a recursive function that modifies the input structure in place.

        Args:
            parsed_structure (dict): The parsed directory structure to preprocess.
        """
        for key, value in parsed_structure.items():
            if isinstance(value, dict):
                value['summary'] = ""
                self._preprocess_structure(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._preprocess_structure(item)

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

    def summarize_directory_structure_api(self, directory_structure: dict, summary_word_length: int, client) -> dict:
        """
        Summarizes the directory structure using the OpenAI API.

        Args:
            directory_structure (dict): The directory structure to summarize.
            summary_word_length (int): The maximum word length for each summary.
            client (OpenAI): The OpenAI client object.

        Returns:
            dict: The summarized directory structure in JSON format with summaries for each file/folder.
        """
        max_tokens = 2048  # Increase the max tokens limit
        temperature = 0.5
        model = "gpt-4o-mini"
        messages = [
            {"role": "system", "content": "You are a directory structure summarizer."},
            {"role": "user", "content": r"Analyze the following directory structure in JSON format where [] represents folders and {} represents files and summarize the purpose of each file in the 'summary' key. Return the JSON object:"},
            {"role": "user", "content": json.dumps(directory_structure)},
            {"role": "user", "content": f"The maximum word length for each summary is {summary_word_length} words."}
        ]
        logger.info(f"Sending request to API for summarization with model: {model}")

        stop_logging.clear()
        logging_thread = threading.Thread(target=log_periodically, args=("Waiting for response from OpenAI API...", 5))
        logging_thread.start()

        try:
            response = client.chat.completions.create(
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