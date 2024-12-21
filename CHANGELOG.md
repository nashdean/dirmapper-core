# Changelog

## [0.2.2] - 2024-12-20
**No Breaking Changes. Safe to Bump**
### DirectoryItem Class
- Add `content_hash` to detect changes to file content

### DirectoryStructure Class
- Added `get_files()` method to return a list of DirectoryItems that are all of metadata type `file`
- Added `get_directories()` method to return a list of DirectoryItems that are all of metadata type `directory`
- Improved `get_files()` method to handle lists of strings for exclusions or inclusions by converting them into `IgnorePattern` objects
- Added error handling and logging for `get_files()` method

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