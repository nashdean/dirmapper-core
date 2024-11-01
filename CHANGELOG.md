# Changelog

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