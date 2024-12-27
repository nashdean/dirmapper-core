# src/dirmapper/ai/summarizer.py
import copy
import os
from typing import List, Optional, Tuple, Dict
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.styles.tree_style import TreeStyle
from dirmapper_core.utils.logger import logger, log_periodically, stop_logging
from dirmapper_core.writer.template_parser import TemplateParser
from openai import OpenAI, AuthenticationError
from dirmapper_core.utils.paginator import DirectoryPaginator
from dirmapper_core.utils.text_analyzer import TextAnalyzer
from dirmapper_core.utils.cache import SummaryCache, cached_api_call

import json
import threading

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import time
from ratelimit import limits, sleep_and_retry


class DirectorySummarizer:
    """
    Class to summarize a directory structure using the OpenAI API or local model.
    """
    def __init__(self, config: dict):
        """
        Initialize the DirectorySummarizer object.

        Args:
            config (dict): Configuration dictionary containing:
                - use_local (bool): Whether to use local summarization.
                - api_token (str): OpenAI API token (required if use_local is False).
                - summarize_file_content (bool): Whether to summarize file contents.
                - max_file_summary_words (int): Maximum words for file content summaries.
                - max_short_summary_characters (int): Maximum characters for short summaries.
                - exclude_files (List[str]): List of files to exclude from summarization.
                - exclude_dirs (List[str]): List of directories to exclude from summarization.
                - exclude_extensions (List[str]): List of file extensions to exclude from summarization.
                - allowed_extensions (List[str]): List of file extensions to allow for summarization.
                - allowed_files (List[str]): List of file names to allow for summarization.
                - pagination_threshold (int): Threshold for pagination (i.e., max items per page allowed).
                - entropy_threshold (float): Threshold for entropy to detect binary content.
                - use_level_pagination (bool): Whether to use level-based pagination.
        """
        self.is_local = config.get('use_local', True)
        self.client = None
        self.summarize_file_content = config.get('summarize_file_content', False)
        self.max_short_summary_characters = config.get('max_short_summary_characters', 75)
        self.max_file_summary_words = config.get('max_file_summary_words', 50)
        self.file_summarizer = FileSummarizer(config)  # Kept this
        self.paginator = DirectoryPaginator(max_items_per_page=config.get('pagination_threshold', 50), max_tokens=4000)
        self.exclude_files = config.get('exclude_files')
        self.exclude_dirs = config.get('exclude_dirs')
        self.exclude_extensions = config.get('exclude_extensions')
        self.allowed_extensions = config.get('allowed_extensions', ['.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.xml', '.js', '.html', '.css', '.go', '.java'])
        self.allowed_files = config.get('allowed_files', ['README', 'MANIFEST', 'LICENSE', 'CHANGELOG', 'CONTRIBUTING', 'Makefile', 'Dockerfile'])
        self.text_analyzer = TextAnalyzer(
            entropy_threshold=config.get('entropy_threshold', 4.0)
        )
        self.use_level_pagination = config.get('use_level_pagination', False)
        self.cache = SummaryCache(
            cache_dir=config.get("cache_dir", ".summary_cache"),
            ttl_days=config.get("cache_ttl_days", 7)
        )
        self.concurrent_dir_summaries = config.get("concurrent_dir_summaries", 3)

        if not self.is_local:
            api_token = config.get("api_token")
            if not api_token:
                raise ValueError("API token is not set. Please set the API token in the preferences.")
            self.client = OpenAI(api_key=api_token)

    def summarize(self, directory_structure: DirectoryStructure) -> dict:
        """
        Summarizes the directory structure using the OpenAI API or local model.

        Args:
            directory_structure (DirectoryStructure): The directory structure to summarize.

        Returns:
            dict: The summarized directory structure with summaries for each file/folder and the project summary.
        """
        if self.is_local:
            logger.warning('Localized summary functionality under construction. Set preferences to use the api by setting `is_local` to False.')
            return {}

        # Get metadata from first item in directory structure
        meta_data = {
            'root_path': directory_structure.items[0].path if directory_structure.items else ''
        }

        logger.info(f"Summarizing directory structure for {len(directory_structure.items)} items.  {len(directory_structure.get_files())} files, {len(directory_structure.get_directories())} directories.")
        summarized_structure = {}
        # Summarize the structure
        summarized_structure['summarized_structure'] = self._summarize_api(directory_structure, meta_data)

        # Merge summaries back into the original structure
        if isinstance(summarized_structure, dict):
            directory_structure.merge_nested_dict(summarized_structure['summarized_structure'])

        # Generate project summary
        project_summary = self.summarize_project(directory_structure)
        
        summarized_structure["project_summary"] = project_summary

        return summarized_structure

    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()

    def _summarize_api(self, directory_structure: DirectoryStructure, meta_data: dict) -> dict:
        """
        Summarizes the directory structure using the OpenAI API with improved caching.
        """
        root_path = meta_data.get('root_path', '')
        
        # Preprocess to add content summaries if enabled
        if self.summarize_file_content:
            self._preprocess_structure(directory_structure)
        
        logger.debug("Preprocessed structure:", directory_structure)
        
        # Check if pagination is needed
        should_paginate, estimated_tokens = self.paginator.should_paginate(directory_structure)
        
        if should_paginate:
            logger.info(f"Directory structure requires pagination. Items: {len(directory_structure.items)}, "
                       f"Estimated tokens: {estimated_tokens}")
            paginated_structures = self.paginator.paginate(
                directory_structure, 
                by_level=self.use_level_pagination
            )
            
            if self.use_level_pagination:
                logger.info(f"Using level-based pagination. Processing {len(paginated_structures)} levels")
            else:
                logger.info(f"Using item-based pagination. Processing {len(paginated_structures)} pages")
            
            summarized_structure = {}
            total_pages = len(paginated_structures)
            
            for idx, paginated_structure in enumerate(paginated_structures, 1):
                # Generate cache key for this page
                page_cache_key = self.cache.get_paginated_structure_key(
                    directory_structure,
                    idx,
                    total_pages
                )
                
                cached_summary = self.cache.get(page_cache_key)
                if cached_summary:
                    logger.info(f"🔵 Using cached summary for page {idx}/{total_pages}")
                    summarized_structure = self._merge_summaries(summarized_structure, cached_summary)
                    continue
                
                if self.use_level_pagination:
                    level = len(paginated_structure.items[0].path.split('/')) - 1 if paginated_structure.items else 0
                    # Try to get cached directory summary for this level
                    items_hash = self.cache._get_contents_hash([item.metadata for item in paginated_structure.items])
                    dir_key = self.cache.get_directory_key(
                        meta_data.get('root_path', ''),
                        items_hash,
                        level
                    )
                    cached_summary = self.cache.get(dir_key)
                    
                    if cached_summary:
                        logger.info(f"🔵 Using cached summary for level {level}")
                        summarized_structure = self._merge_summaries(summarized_structure, cached_summary)
                        continue
                    
                    # Cache parent context if available
                    if level > 0:
                        parent_items = [item for item in directory_structure.items if item.level < level]
                        parent_key = self.cache.get_parent_context_key(
                            meta_data.get('root_path', ''),
                            level - 1
                        )
                        self.cache.set(parent_key, {
                            'items': [item.metadata for item in parent_items],
                            'level': level - 1
                        })
                
                # Log the first few items in this batch for context
                sample_items = [item.path for item in paginated_structure.items[:3]]
                logger.debug(f"Sample items in current batch: {', '.join(sample_items)}")
                
                partial_summary = self._summarize_directory_structure_api(
                    paginated_structure,
                    self.max_short_summary_characters     
                )
                
                # Cache the page summary
                if partial_summary:
                    self.cache.set(page_cache_key, partial_summary)
                
                summarized_structure = self._merge_summaries(summarized_structure, partial_summary)
                logger.info(f"Completed processing batch {idx}/{total_pages}")
            
            return summarized_structure
        else:
            logger.info(f"Processing directory structure without pagination. Items: {len(directory_structure.items)}, "
                       f"Estimated tokens: {estimated_tokens}")
            return self._summarize_directory_structure_api(
                directory_structure, 
                self.max_short_summary_characters
            )

    def _preprocess_structure(self, structure: DirectoryStructure) -> None:
        """
        Preprocesses the directory structure to add content summaries in parallel.
        """
        # Get all files that need summarization
        files_to_summarize = [
            item for item in structure.get_files()
            if not self._is_empty_or_near_empty(item.content) 
            and self._should_summarize_file(item.path, item.content)
        ]

        if not files_to_summarize:
            return

        logger.info(f"Summarizing {len(files_to_summarize)} files in parallel...")
        
        # Process files in parallel using FileSummarizer
        summaries = self.file_summarizer.summarize_items_parallel(
            files_to_summarize,
            self.max_file_summary_words
        )

        logger.info(f"Completed summarizing {len(summaries)} files")

    def _is_empty_or_near_empty(self, content: Optional[str]) -> bool:
        """
        Check if the content is empty or near-empty.

        Args:
            content (Optional[str]): The content to check.

        Returns:
            bool: True if the content is empty or near-empty, False otherwise.
        """
        return content is None or len(content.strip()) == 0

    def _should_summarize_file(self, file_path: str, content: Optional[str] = None) -> bool:
        """
        Determines if a file should be summarized based on its extension and content characteristics.

        Args:
            file_path (str): The path to the file.
            content (Optional[str]): The content of the file.

        Returns:
            bool: True if the file should be summarized, False otherwise.
        """
        if self.exclude_files and os.path.basename(file_path) in self.exclude_files:
            return False
        if self.exclude_dirs and os.path.dirname(file_path) in self.exclude_dirs:
            return False
        if self.exclude_extensions and os.path.splitext(file_path)[1] in self.exclude_extensions:
            return False
        
        # Check file extension and name
        _, ext = os.path.splitext(file_path)
        file_name = os.path.basename(file_path)
        if ext.lower() in self.allowed_extensions or file_name in self.allowed_files:
            # Even if extension is allowed, check if content is binary
            print("checking:", file_name)
            return not (content and self.text_analyzer.is_binary_content(content))
        
        return False

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

    @cached_api_call
    def _summarize_directory_structure_api(self, directory_structure: DirectoryStructure, short_summary_length: int) -> dict:
        """
        Summarizes the directory structure using the OpenAI API.

        Args:
            directory_structure (DirectoryStructure): The directory structure to summarize.
            short_summary_length (int): The maximum word length for each summary.

        Returns:
            dict: The summarized directory structure in JSON format with summaries for each file/folder.
        """
        # Add parent context to improve summaries
        parent_context = None
        if self.use_level_pagination:
            level = len(directory_structure.items[0].path.split('/')) - 1 if directory_structure.items else 0
            if level > 0:
                parent_key = self.cache.get_parent_context_key(
                    directory_structure.items[0].path,
                    level - 1
                )
                parent_context = self.cache.get(parent_key)

        # Set cache context for the decorator using directory structure's content hash
        self.cache_context = f"structure_{directory_structure.content_hash}"
        if parent_context:
            self.cache_context += f"_level_{parent_context.get('level', '')}"

        simple_json_structure = directory_structure.to_nested_dict(['type', 'short_summary'])
        tree_structure = TreeStyle.write_structure(directory_structure)
        
        messages = [
            {
                "role": "system",
                "content": "You are a directory structure analyzer. Respond only with valid JSON."
            }
        ]

        # Add parent context if available
        if parent_context:
            messages.append({
                "role": "system",
                "content": f"Parent directory context: {json.dumps(parent_context)}"
            })

        messages.append({
            "role": "user", 
            "content": (
                "Analyze the following directory structure:\n\n"
                f"{tree_structure}\n\n"
                "Use the following JSON object that matches the input structure to generate "
                "`short_summary` fields overwriting the existing `short_summary` field. Use the existing `short_summary` value "
                "for additional context about the existing file if it is not labled 'Empty File'. Generate a short summary for "
                "each folder based on the files it contains and also store this in the field `short_summary`. "
                f"Do not modify the structure in any other way. Write each short summary in {short_summary_length} characters "
                f"or less. Here is the formatted JSON:\n\n{json.dumps(simple_json_structure, indent=2)}"
            )
        })
        logger.info("Sending request to API for summarization...")
        logger.info(f"Structure contains {len(directory_structure.items)} items "
                   f"({len(directory_structure.get_files())} files, "
                   f"{len(directory_structure.get_directories())} directories)")

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
                max_tokens=4096,
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
                logger.error(f"JSON Parse Error at position {e.pos}: {raw_response[max(0, e.pos-200):e.pos+200]}")
                return directory_structure
                
        except Exception as e:
            logger.error(f"API Error: {str(e)}")
            return directory_structure
            
        finally:
            stop_logging.set()
            logging_thread.join()
    
    def _merge_summaries(self, original: dict, new: dict) -> dict:
        """
        Merges two dictionaries of summaries as a deep merge.

        Args:
            original (dict): The original dictionary of summaries.
            new (dict): The new dictionary of summaries to merge.

        Returns:
            dict: Returns the merged dictionary of summaries (which is also mutated in place).
        """
        for key, value in new.items():
            if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                original[key] = self._merge_summaries(original[key], value)
            else:
                original[key] = value
        return original
    
    def summarize_project(self, directory_structure: DirectoryStructure) -> str:
        """
        Generates a summary of the entire project based on the directory structure.

        Args:
            directory_structure (DirectoryStructure): The directory structure of the project.

        Returns:
            str: The summary of the entire project.
        """
        # Set cache context using the cache manager's project key generation
        self.cache_context = self.cache.get_project_summary_key(directory_structure)
        
        # Aggregate summaries
        aggregated_summaries = self._aggregate_summaries(directory_structure)

        # Generate project summary using OpenAI API
        project_summary = self._generate_project_summary(aggregated_summaries)

        # Update directory structure with project summary
        directory_structure.description = project_summary

        return project_summary

    @cached_api_call
    def _generate_project_summary(self, aggregated_summaries: str) -> str:
        """
        Generates a project summary using the OpenAI API based on aggregated summaries.

        Args:
            aggregated_summaries (str): The aggregated summaries as a single string.

        Returns:
            str: The project summary.
        """
        prompt = (
            "Generate a concise summary of the following project based on the provided summaries:\n\n"
            f"{aggregated_summaries}\n\n"
            "Summarize the project in a few sentences."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an assistant that generates project summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )

            project_summary = response.choices[0].message.content.strip()
            return project_summary
        except Exception as e:
            logger.error(f"Error generating project summary: {str(e)}")
            return "Error generating project summary."

    def _aggregate_summaries(self, directory_structure: DirectoryStructure) -> str:
        """
        Aggregates individual summaries into a single string.

        Args:
            directory_structure (DirectoryStructure): The summarized directory structure.

        Returns:
            str: The aggregated summaries as a single string.
        """
        summaries = []
        
        # Get all items that have summaries
        for item in directory_structure.items:
            if item.short_summary:
                summaries.append(f"{item.path}: {item.short_summary}")
        
        return "\n".join(summaries)

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
        self.max_file_summary_words = config.get("max_file_summary_words", 50)
        self.max_short_summary_characters = config.get("max_short_summary_characters", 75)
        self.client = None
        if not self.is_local:
            api_token = config.get("api_token")
            if not api_token:
                raise ValueError("API token is not set. Please set the API token in the preferences.")
            self.client = OpenAI(api_key=api_token)
        self.max_workers = config.get("max_workers", 5)
        self.requests_per_minute = config.get("requests_per_minute", 50)
        self.batch_size = config.get("batch_size", 10)
        self.cache = SummaryCache(
            cache_dir=config.get("cache_dir", ".summary_cache"),
            ttl_days=config.get("cache_ttl_days", 7)
        )
        self.chunk_size = config.get("chunk_size", 4000)
        self.concurrent_chunks = config.get("concurrent_chunks", 3)

    @sleep_and_retry
    @limits(calls=50, period=60)  # Rate limit: 50 calls per minute
    def _rate_limited_api_call(self, messages: List[Dict], model: str, max_tokens: int, temperature: float) -> Any:
        """Make a rate-limited API call to OpenAI."""
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
    
    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()

    def summarize_items_parallel(self, items: List[DirectoryItem], max_words: int = 100) -> Dict[str, Dict]:
        """
        Summarize multiple DirectoryItems in parallel.

        Args:
            items (List[DirectoryItem]): List of DirectoryItems to summarize
            max_words (int): Maximum words per summary

        Returns:
            Dict[str, Dict]: Dictionary mapping file paths to their summaries
        """
        if self.is_local:
            logger.warning('Local summarization is not implemented yet.')
            return {item.path: {"summary": "", "short_summary": ""} for item in items}

        # Filter out items that don't need summarization
        items_to_summarize = [
            item for item in items 
            if item.metadata.get('type') == 'file' 
            and (not item.summary or item.content_hash != item.metadata.get('content_hash'))
        ]

        if not items_to_summarize:
            return {}

        # Process items in batches to avoid overwhelming the API
        results = {}
        for i in range(0, len(items_to_summarize), self.batch_size):
            batch = items_to_summarize[i:i + self.batch_size]
            batch_results = self._process_batch(batch, max_words)
            results.update(batch_results)
            
            # Small delay between batches to help with rate limiting
            if i + self.batch_size < len(items_to_summarize):
                time.sleep(1)

        return results

    def _process_batch(self, items: List[DirectoryItem], max_words: int) -> Dict[str, Dict]:
        """
        Process a batch of items using a thread pool.

        Args:
            items (List[DirectoryItem]): Batch of items to process
            max_words (int): Maximum words per summary

        Returns:
            Dict[str, Dict]: Dictionary mapping file paths to their summaries
        """
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {
                executor.submit(self._summarize_item, item, max_words): item
                for item in items
            }

            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    summary_result = future.result()
                    if summary_result:
                        results[item.path] = summary_result
                        # Update the item with new summaries
                        item.summary = summary_result.get('summary', '')
                        item.short_summary = summary_result.get('short_summary', '')
                        item.metadata['content_hash'] = item.content_hash
                except Exception as e:
                    logger.error(f"Error processing {item.path}: {str(e)}")
                    results[item.path] = {"summary": "", "short_summary": ""}

        return results

    def _summarize_item(self, item: DirectoryItem, max_words: int) -> Dict[str, str]:
        """
        Summarize a single DirectoryItem.

        Args:
            item (DirectoryItem): Item to summarize
            max_words (int): Maximum words in summary

        Returns:
            Dict[str, str]: Dictionary containing summary and short_summary
        """
        try:
            if not item.content:
                return {"summary": "", "short_summary": ""}

            if len(item.content) > 5000:
                return self._summarize_large_content(item.name, item.content, max_words)
            else:
                return self._summarize_purpose_api(item.name, item.content, max_words)
        except Exception as e:
            logger.error(f"Error summarizing {item.path}: {str(e)}")
            return {"summary": "", "short_summary": ""}

    def summarize_content(self, item: DirectoryItem, max_words: int = 100, force_refresh: bool = False) -> dict:
        """
        Summarizes the content using the OpenAI API or local model.

        Args:
            item (DirectoryItem): The content to summarize.
            max_words (int): The maximum number of words for the summary.
            force_refresh (bool): Whether to force refresh the cache.

        Returns:
            dict: The summarized content with the summary and short summary.
        """
        # Compute content hash
        content_hash = item.content_hash

        # Get content
        content = item.content
        if content is None:
            return {}

        # Check if the file should be summarized
        if not force_refresh and item.summary and item.content_hash == content_hash:
            logger.info(f"Using cached summary for {item.name}")
            return {'summary': item.summary, 'short_summary': item.short_summary}

        if self.is_local:
            logger.warning('Local summarization is not implemented yet.')
            return {"summary": "Local summarization is not implemented yet.", "short_summary": ""}
        else:
            # Check content size
            max_content_length = 5000  # Adjust based on API limits
            if len(content) > max_content_length:
                logger.info(f"File is large; summarizing in chunks. Summarizing {item.name or 'content'}...")
                summary_dict = self._summarize_large_content(item.name, content, max_words)
                summary = summary_dict.get('summary', '')
                short_summary = summary_dict.get('short_summary', '')
            else:
                summary_dict = self._summarize_purpose_api(item.name, content, max_words)
                summary = summary_dict.get('summary', '')
                short_summary = summary_dict.get('short_summary', '')
            
            item.summary = summary
            item.short_summary = short_summary  # Add short summary
            item.content_hash = content_hash  # Update the hash in the item
            return {'summary': summary, 'short_summary': short_summary}

    def summarize_file(self, file_path: str, max_words: int = 100) -> dict:
        """
        Summarizes the content of a file.

        Args:
            file_path (str): The path to the file to summarize.
            max_words (int): The maximum number of words for the summary.

        Returns:
            dict: The summarized content with the summary and short summary.
        """
        if not os.path.isfile(file_path):
            logger.error(f"File not found: {file_path}")
            return {"summary": "", "short_summary": ""}

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {"summary": "", "short_summary": ""}

        if self.is_local:
            logger.warning('Local summarization is not implemented yet.')
            return {"summary": "Local summarization is not implemented yet.", "short_summary": ""}
        else:
            file_name = os.path.basename(file_path)
            # Check content size
            max_content_length = 5000  # Adjust based on API limits
            if len(content) > max_content_length:
                logger.info(f"File is large; summarizing in chunks. Summarizing {file_name}...")
                return self._summarize_large_content(content, max_words)
            else:
                return self._summarize_purpose_api(file_name, content, max_words)

    def _summarize_large_content(self, file_name: str, content: str, max_words: int) -> dict:
        """
        Summarizes large content by splitting it into chunks.

        Args:
            file_name (str): The name of the file.
            content (str): The content to summarize.
            max_words (int): The maximum number of words for the summary.

        Returns:
            dict: The combined summary of all chunks and a short summary.
        """
        chunks = [content[i:i + self.chunk_size] for i in range(0, len(content), self.chunk_size)]
        total_chunks = len(chunks)
        summaries = []

        with ThreadPoolExecutor(max_workers=self.concurrent_chunks) as executor:
            futures = []
            for idx, chunk in enumerate(chunks):
                chunk_key = self.cache.get_chunk_key(file_name, idx, total_chunks)
                cached_result = self.cache.get(chunk_key)
                
                if cached_result:
                    logger.info(f"🔵 Using cached chunk {idx + 1}/{total_chunks} for {file_name}")
                    summaries.append(cached_result.get('summary', ''))
                    continue

                future = executor.submit(
                    self._summarize_chunk,
                    chunk_key,
                    file_name,
                    chunk,
                    max_words,
                    idx,
                    total_chunks
                )
                futures.append(future)

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result and result.get('summary'):
                        summaries.append(result['summary'])
                except Exception as e:
                    logger.error(f"Error processing chunk: {str(e)}")

        # Combine and summarize
        if not summaries:
            return {"summary": "", "short_summary": ""}

        combined_summary = "\n".join(summaries)
        final_key = self.cache.get_chunk_key(file_name, -1, total_chunks)  # Special key for final summary
        
        cached_final = self.cache.get(final_key)
        if cached_final:
            logger.info(f"🔵 Using cached final summary for {file_name}")
            return cached_final

        # Generate final summaries
        final_result = self._summarize_purpose_api(file_name, combined_summary, max_words)
        if final_result:
            self.cache.set(final_key, final_result)

        return final_result

    def _summarize_chunk(self, chunk_key: str, file_name: str, chunk: str, 
                        max_words: int, chunk_idx: int, total_chunks: int) -> Dict[str, str]:
        """Summarize a single chunk with caching."""
        try:
            cached_result = self.cache.get(chunk_key)
            if cached_result:
                logger.info(f"🔵 Using cached chunk {chunk_idx + 1}/{total_chunks} for {file_name}")
                return cached_result

            logger.info(f"🔄 Processing chunk {chunk_idx + 1}/{total_chunks} for {file_name}")
            result = self._summarize_purpose_api(
                f"{file_name}_chunk_{chunk_idx}",
                chunk,
                max_words
            )
            
            if result and result.get('summary'):
                self.cache.set(chunk_key, result)
            
            return result
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_idx + 1}/{total_chunks}: {str(e)}")
            return {"summary": "", "short_summary": ""}

    @cached_api_call
    def _summarize_purpose_api(self, file_name: str, content: str, max_length: int, is_short: bool=False) -> dict:
        """
        Summarizes the content using the OpenAI API.

        Args:
            file_name (str): The name of the file.
            content (str): The content to summarize.
            max_length (int): The maximum length for the summary (words or characters).
            is_short (bool): Whether the summary is a short summary.

        Returns:
            dict: The summarized content with the summary and short summary.
        """
        max_tokens = 2048
        temperature = 0.5
        model = "gpt-4o-mini"

        # Prepare the prompt
        messages = [
            {"role": "system", "content": "You are a helpful assistant that summarizes file content into markdown format."},
            {"role": "user", "content": (
                f"Please provide a JSON response with both a long summary and a short summary of the following file content. "
                "The long summary should be a brief description of the content, and the short summary should be a concise version of the long summary. "
                "Explain the purpose of the content and any key points. "
                f"The long summary should be limited to {self.max_file_summary_words} words and the short summary should be limited to {self.max_short_summary_characters} characters. "
                "Short summaries should not have any new lines. Return the summaries in the following format:\n\n"
                f"{{\n  \"summary\": \"This is the long summary.\",\n  \"short_summary\": \"This is the short summary.\"\n}}"
                f"Do not include any additional information in the response. Here is the content for the file {file_name}:\n\n"
                f"{content}"
            )}
        ]

        logger.info(f"🔄 Processing summary request for {file_name}...")

        stop_logging.clear()
        logging_thread = threading.Thread(target=log_periodically, args=("Waiting for response from OpenAI API...", 5))
        logging_thread.start()

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            logger.info(f"✅ Received API response for {file_name}")
            if not response or not response.choices:
                logger.error("Empty or invalid response from API")
                return {"summary": "", "short_summary": ""}

            summary_response = response.choices[0].message.content.strip()
            try:
                summary_dict = json.loads(summary_response)
                return {
                    "summary": summary_dict.get("summary", ""),
                    "short_summary": summary_dict.get("short_summary", "")
                }
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON response from API")
                return {"summary": "", "short_summary": ""}
        except AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return {"summary": "", "short_summary": ""}
        except Exception as e:
            logger.error(f"❌ API Error for {file_name}: {str(e)}")
            return {"summary": "", "short_summary": ""}
        finally:
            stop_logging.set()
            logging_thread.join()