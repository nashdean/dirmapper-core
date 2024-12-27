# Changelog

## [0.2.4] - 2024-12-27 : Pre-Release
**No Breaking Changes. Safe to Bump**
**Full Changelog**: [v0.2.3...v0.2.4](https://github.com/nashdean/dirmapper-core/compare/v0.2.3...v0.2.4)

### Performance Improvements
- Added disk-based caching for API responses to reduce redundant calls
- Implemented concurrent processing for directory level summarization
- Optimized large file processing with parallel chunk summarization
- Added TTL-based cache expiration to ensure freshness of summaries
- Improved batch processing with dynamic chunk sizes

### Cache Module
- Added new `cache.py` module in utils for centralized caching functionality
- Moved SummaryCache class and cached_api_call decorator from summarizer.py
- Added improved error handling and logging for cache operations
- Implemented clean separation of concerns for caching logic
- Added cache performance monitoring and statistics
- Improved logging with clear visual indicators for cache hits/misses
- Added periodic cache statistics reporting
- Added emoji indicators for better log readability

### Cache Improvements
- Extended cache TTL to 30 days for better persistence
- Added content normalization to increase cache hits
- Implemented consistent chunk caching for large files
- Added intelligent cache key generation
- Improved handling of path variations in cache keys
- Added chunk-level caching for better granularity
- Added directory-level caching for better performance
- Implemented parent context caching for improved summaries
- Added smart invalidation based on directory content hashes
- Enhanced cache keys with level-based directory context
- Improved caching granularity for directory structures

### DirectoryStructure Class
- Added content_hash property for directory structure caching
- Added level-based hash calculation for granular caching
- Improved hash consistency with sorted items
- Added hash invalidation on structure changes
- Added project level summarization for directory structures by combining file summaries

### ContentGenerator Class
- Introduced `ContentGenerator` class for generating file content using OpenAI API.
- Added methods for building prompts and generating content based on directory structure.
- Improved content generation with context-aware prompts.

### AI Module Documentation
- Added new `README.md` in dirmapper_core/ai folder
- Documented usage of `DirectorySummarizer` and `FileSummarizer` classes
- Explained caching mechanism and how it is incorporated
- Detailed parallelization techniques used in summarization
- Provided examples for using the summarizers and clearing the cache

### Formatter Refactoring
- Created new `BaseFormatter` class in separate file
- Moved formatter implementations to depend on style objects passed through instructions
- Removed direct style imports from formatter.py to fix circular dependencies
- Improved separation of concerns between formatters and styles

### Dependency Resolution
- Added new ContentService class to handle content generation
- Moved content generation logic out of JSONStyle to break circular dependencies
- Improved separation of concerns between styles and AI content generation

### Miscellaneous
- Updated README with fixes.

## [0.2.3] - 2024-12-22 : Pre-release
**No Breaking Changes. Safe to Bump**
**Full Changelog**: [v0.2.2...v0.2.3](https://github.com/nashdean/dirmapper-core/compare/v0.2.2...v0.2.3)
### DirectorySummarizer Class
- Updated to pass the max word length and max short summary length variables to the FileSummarizer.
- Updated to only use the existing short summaries to generate the project contextual short summaries for each file.
- Added functionality to fill in the blanks for files/directories still missing short summaries without including long summaries in the API call.
- Added pagination for large directory structures using the new `DirectoryPaginator` class.
    - Added configuration option for level-based pagination
    - Updated summarizer to support processing directory structures level by level
    - Improved pagination logging to show detailed progress:
        - Added page/level numbers and total count
        - Added item counts per batch
        - Added sample items being processed
        - Added clearer distinction between level-based and item-based pagination
        - Added completion status for each batch
- Skipped summarization for empty or near-empty files.
- Refactored `_should_summarize_file` to use new `TextAnalyzer` utility class
- Improved file content analysis with better separation of concerns

### FileSummarizer Class
- Modified to return both "summary" and "short_summary" in the same API call to reduce cost and response time.
- Updated the prompt and API to return a JSON formatted response with the content summary applied to the key "summary" and the short summary to the key "short_summary".
- Refactored code to validate this return value structure.
- For larger content that is divided into chunks, the short summary is only generated on the final iteration where the summary is combined.
- Added file names to the API prompt for further context

### DirectoryPaginator Class
- Created a new `DirectoryPaginator` class to handle pagination of large directory structures into smaller chunks.
- Added level-based pagination support to process directory structures level by level
- Added method to extract and maintain parent directory context in level-based pagination
- Updated paginate method to support both item-count and level-based pagination modes

### TextAnalyzer Utility
- Added new `TextAnalyzer` utility class for analyzing text content characteristics
- Added configurable entropy threshold for binary content detection
- Added comprehensive list of common text file patterns for better file type detection

### Logger
- Added more detailed `INFO` logs including directory size and files being summarized (optional argument).

### Miscellaneous
- Updated README with fixes.

## [0.2.2] - 2024-12-20 : Pre-release
**No Breaking Changes. Safe to Bump**
### DirectoryItem Class
- Add `content_hash` to detect changes to file content

### DirectoryStructure Class
- Added `get_files()` method to return a list of DirectoryItems that are all of metadata type `file`
- Added `get_directories()` method to return a list of DirectoryItems that are all of metadata type `directory`
- Improved `get_files()` method to handle lists of strings for exclusions or inclusions by converting them into `IgnorePattern` objects
- Added error handling and logging for `get_files()` method
- Added `use_json_style` parameter to `to_nested_dict()` method allowing use of richer JSONStyle format while maintaining backward compatibility

### PathIgnorer Class
- Refactored to manage ignoring patterns without focusing on root directories
- Removed root directory specific logic

### Logger
- Updated `log_ignored_paths()` method to show the total overall ignored files and folders instead of just the root

### Summarization
- Added more detailed `INFO` logs including directory size and files being summarized (optional argument)
- Cache summaries by checking if the DirectoryItem's `content_hash` has changed

## [0.2.1] - 2024-12-17
**No Breaking Changes. Safe to Bump**
### Directory Parser
- Renamed `parse_template` to `parse_from_template_file`. Old method still valid until **v0.3.0**
- Renamed `parse_from_directory_structure` to `parse_from_style`. Old method still valid until **v0.3.0**.
- Added `template_to_directory_structure` method to convert templates to DirectoryStructure objects

### DirectoryItem Class
- Changed order in which how Metadata appears in dict

### Style Changes
- Changed the value for the meta field `type` from `folder` to `directory` in JSONStyle to match the expected values of DirectoryItem class
- Added `write_structure_with_short_summaries` method to TreeStyle that formats `short_summary` field that is generated from the DirectorySummarizer next to each file/folder branch as a nicely formatted comment delimited by `#`
    - Formats nicely to the console/terminal for easy human readability
    - **NOTE**: Function may be renamed as it gets extended to other styles in the future

## [0.2.0] - 2024-12-15
**No Breaking Changes. Safe to Bump**
### Directory Writer
- Updated to add a safety by default to `structure_writer.py`'s function `write_structure`. Prompts user to enter if they wish to continue. This helps to avoid accidently overwriting files/folders if this is not desired.
- Updated the `write_structure` to skip the key `__keys__` in the templates

### AI Changes
- Created `FileSummarizer` class to summarize individual files via OpenAI API
- Updated `DirectorySummarizer` class to include file summarization as part of the process for summarizing directories
    - Updates the DirectoryItem objects and DirectoryStructure object with the `summary` and `short_summary` respectively

### Template Changes
- Updated expected template format so that structure is always only dicts
    - folders are specified and recognized by a `/` forward slash appended to the end, otherwise assumed to be a file
- Fixed writing a JSON/YAML template from a formatted directory structure string for `template_writer.py`'s function `write_template`
- The `meta` tags now include `root_path` as a field for specifying the path to write/read a directory structure. If not set or set to None, reads/writes will default to the current working directory.

### Style Changes
- Changed `IndentationStyle` to be same style without the tree characters
- Updated `write_structure` in `JSONStyle` to follow the expected format of the JSON Template to include special key `__keys__`
- Updated `JSONStyle` to have `json_to_structure` function to convert JSON back into a list of tuples
- Made all styles static since they do not carry state

### Models
- Abstracted the generic structure from `Tuple[str, int, str]` into a `DirectoryItem` class to make it more extensible
    - Added a metadata attribute to class that can be used for the `summarize` to get a `summary` element
- Abstracted the `List[Tuple[str, int, str]]` into its own class which is essentially a List of `DirectoryItem` objects
    - Added multiple custom methods that could be useful in future

### Miscellaneous
- Updated README with fixes


## [0.1.0] - 2024-11-01
**Breaking Changes to Imports**
- Reorganized/Modified module structure for ignore, utils, writer
    - Moved modules around and changed names to logically make more sense
- Fixed minor bugs
    - Package now includes the `.mapping-ignore` for baseline ignore patterns (was missing in `v0.0.4`)
    - Resolved circular import error in `logger.py` caused by type checking

## [0.0.4] - 2024-10-31
**No Breaking Changes. Safe to Bump**
- Update all functions, classes, and methods with improved documentation
- Fix `~` edge case to expand to home directory and not throw an error in `directory_structure_generator.py`
- Refactored `structure_writer.py` for future file/folder type expansion (i.e. webscraping, github)
    - Fix `~` edge case in `structure_writer.py` to reference home directory instead of reading the tilda as a literal
    - `create_structure()` now stores the metadata and structure of a template
    - `build_structure()` now executes writing the structure to the specified OS directory path
- Added improved Makefile to install library locally
- Update `writer.py` to catch *FileNotFound* errors and default to creating intermediary directories if they do not exist where the template file is to be written
- Fix README.md examples
- Small changes to console log messages

## [0.0.3] - 2024-10-30
- Ported over CLI logic, abstracting it into `dirmapper-core` library
    - See Dirmap-CLI's [CHANGELOG.md](https://github.com/nashdean/dirmap-cli/blob/master/CHANGELOG.md) v1.1.0 for details
