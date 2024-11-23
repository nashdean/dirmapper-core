# Changelog

## [0.1.1] - 2024-11-01
**No Breaking Changes. Safe to Bump**
- Created `FileSummarizer` class to summarize individual files via OpenAI API
- Updated `DirectorySummarizer` class to include file summarization as part of the process for summarizing directories. Stores file summaries in a `summary` key in JSON formatted object during pre-processing -- this is currently overwritten by the Directory Summary which does not consider the file content during `DirectorySummarizer`'s summarization (`DirectorySummarizer` summarize function only considers file name currently for context.)
- Updated expected template format so that structure is always only dicts
    - folders are specified and recognized by a `/` forward slash appended to the end, otherwise assumed to be a file
- Fixed writing a JSON/YAML template from a formatted directory structure string for `template_writer.py`'s function `write_template`
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