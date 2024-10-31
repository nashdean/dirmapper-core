# dirmapper-core
A directory mapping library that aids in visualization and directory structuring.
# dirmapper-core

A directory mapping library that aids in visualization and directory structuring.

## Features

- Generate directory structures in various styles (tree, list, flat, etc.)
- Apply custom formatting to directory structures (plain text, JSON, HTML, Markdown, etc.)
- Ignore specific files and directories using patterns
- Summarize directory contents using AI (local or API-based)

## Installation

To install the library, use pip:

```sh
pip install dirmapper-core
```

## Usage
### Generating Directory Structure
You can generate a directory structure using the DirectoryStructureGenerator class. Here is an example:
```python
from dirmapper_core.generator.directory_structure_generator import DirectoryStructureGenerator
from dirmapper_core.ignore.path_ignorer import PathIgnorer
from dirmapper_core.styles.tree_style import TreeStyle
from dirmapper_core.formatter.formatter import PlainTextFormatter

# Define ignore patterns
ignore_patterns = [
    SimpleIgnorePattern('.git/'),
    SimpleIgnorePattern('.github/'),
    SimpleIgnorePattern('__pycache__/')
]

# Initialize PathIgnorer
path_ignorer = PathIgnorer(ignore_patterns)

# Initialize DirectoryStructureGenerator
generator = DirectoryStructureGenerator(
    root_dir='path/to/your/project',
    output='output.txt',
    ignorer=path_ignorer,
    sort_order='asc',
    style=TreeStyle(),
    formatter=PlainTextFormatter()
)

# Generate and save the directory structure
generator.generate()
```
### Summarizing Directory Structure
You can summarize the directory structure using the `DirectorySummarizer` class. Here is an example:
