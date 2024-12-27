# AI Module Documentation

This module integrates with the OpenAI API to provide summarization capabilities for directory structures and individual files. It includes three main components: `DirectorySummarizer`, `FileSummarizer`, and `ContentGenerator`.

## DirectorySummarizer

The `DirectorySummarizer` class is designed to summarize an entire directory structure, including its files and subdirectories.

### Usage

```python
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.ai.summarizer import DirectorySummarizer

# Configuration dictionary
config = {
    'use_local': False,
    'api_token': 'your_openai_api_token',
    'summarize_file_content': True,
    'max_file_summary_words': 50,
    'max_short_summary_characters': 75,
    'exclude_files': ['.gitignore'],
    'exclude_dirs': ['.git'],
    'exclude_extensions': ['.log'],
    'allowed_extensions': ['.py', '.md', '.txt'],
    'allowed_files': ['README.md'],
    'pagination_threshold': 50,
    'entropy_threshold': 4.0,
    'use_level_pagination': True,
    'cache_dir': '.summary_cache',
    'cache_ttl_days': 30,
    'concurrent_dir_summaries': 3
}

# Initialize the summarizer
directory_summarizer = DirectorySummarizer(config)

# Create a DirectoryStructure object
directory_structure = DirectoryStructure()
# Add items to the directory structure
# directory_structure.add_item(...)

# Summarize the directory structure
summary = directory_summarizer.summarize(directory_structure)
print(summary)
```

### Methods

- `summarize(directory_structure: DirectoryStructure) -> dict`: Summarizes the given directory structure and returns a dictionary with the summarized structure and project summary.
- `clear_cache()`: Clears the cache.
- `summarize_project(directory_structure: DirectoryStructure) -> str`: Generates a summary of the entire project based on the directory structure.

## FileSummarizer

The `FileSummarizer` class is designed to summarize individual files.

### Usage

```python
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.ai.summarizer import FileSummarizer

# Configuration dictionary
config = {
    'use_local': False,
    'api_token': 'your_openai_api_token',
    'max_file_summary_words': 50,
    'max_short_summary_characters': 75,
    'cache_dir': '.summary_cache',
    'cache_ttl_days': 30,
    'max_workers': 5,
    'requests_per_minute': 50,
    'batch_size': 10,
    'chunk_size': 4000,
    'concurrent_chunks': 3
}

# Initialize the summarizer
file_summarizer = FileSummarizer(config)

# Create a DirectoryItem object
directory_item = DirectoryItem(path='example.txt', type='file', content='This is an example file content.')

# Summarize the file content
summary = file_summarizer.summarize_content(directory_item)
print(summary)
```

### Methods

- `summarize_content(item: DirectoryItem, max_words: int = 100, force_refresh: bool = False) -> dict`: Summarizes the content of the given directory item.
- `summarize_file(file_path: str, max_words: int = 100) -> dict`: Summarizes the content of the file at the given path.
- `clear_cache()`: Clears the cache.

## Content Generator

The `ContentGenerator` class provides functionality to generate content for files based on the directory structure and its items.

### Usage

```python
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.ai.content_generator import ContentGenerator

# Initialize the content generator
content_generator = ContentGenerator(api_key='your_openai_api_key')

# Create a DirectoryStructure object
directory_structure = DirectoryStructure()
# Add items to the directory structure
# directory_structure.add_item(...)

# Generate content for a specific file
generated_content = content_generator.generate_file_content('example.txt', directory_structure)
print(generated_content)
```

### Methods

- `generate_file_content(path: str, directory_structure: DirectoryStructure) -> str`: Generates content for the specified file based on the directory structure and its items.

## Caching

Both `DirectorySummarizer` and `FileSummarizer` use a caching mechanism to avoid redundant API calls and improve performance. The caching is handled by the `SummaryCache` class, which stores summaries in a disk-based cache with a configurable TTL (time-to-live).

### How Caching Works

1. **Cache Initialization**: The cache is initialized with a specified directory and TTL.
2. **Cache Key Generation**: Unique cache keys are generated based on the content and context of the directory or file being summarized.
3. **Cache Retrieval**: Before making an API call, the cache is checked for an existing summary using the generated cache key.
4. **Cache Storage**: If no cached summary is found, the API call is made, and the result is stored in the cache with the generated key.
5. **Cache Clearing**: The cache can be cleared manually using the `clear_cache` method.

More details on caching can be found in the wiki documentation here: [Caching Mechanism](https://github.com/nashdean/dirmapper-core/wiki/Improving-Responsive-Performance-with-Caching)

### Example

```python
# Clear the cache
directory_summarizer.clear_cache()
file_summarizer.clear_cache()
```

## Parallelization

Both `DirectorySummarizer` and `FileSummarizer` utilize parallelization to improve performance and reduce processing time.

### DirectorySummarizer

- **Concurrent Directory Summarization**: The `DirectorySummarizer` class can process multiple directory levels concurrently using the `concurrent_dir_summaries` configuration option.
- **Level-Based Pagination**: When summarizing large directory structures, the `DirectorySummarizer` can paginate the structure by levels and process each level in parallel.

### FileSummarizer

- **Parallel File Summarization**: The `FileSummarizer` class can summarize multiple files in parallel using a thread pool. The number of concurrent workers is controlled by the `max_workers` configuration option.
- **Chunk-Based Summarization**: For large files, the `FileSummarizer` splits the content into chunks and processes each chunk in parallel. The chunk size and number of concurrent chunks are configurable.

### Example

```python
# DirectorySummarizer uses FileSummarizer to summarize files within the directory structure
directory_summarizer = DirectorySummarizer(config)
directory_structure = DirectoryStructure()
# Add items to the directory structure
# directory_structure.add_item(...)

# Summarize the directory structure
summary = directory_summarizer.summarize(directory_structure)
print(summary)
```

This documentation provides an overview of how to use the `DirectorySummarizer`, `FileSummarizer`, and `ContentGenerator` classes, how caching is incorporated, and how these components interact.
