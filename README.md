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
You can generate a directory structure using the `DirectoryStructureGenerator` class. Here is an example:
```python
from dirmapper_core.generator.directory_structure_generator import DirectoryStructureGenerator
from dirmapper_core.ignore.path_ignorer import PathIgnorer
from dirmapper_core.ignore.ignore_list_reader import SimpleIgnorePattern
from dirmapper_core.styles.tree_style import TreeStyle
from dirmapper_core.formatter.formatter import PlainTextFormatter
from dirmapper.utils.sorting_strategy import AscendingSortStrategy

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
    root_dir='./path/to/your/directory',
    output='output.txt',
    ignorer=path_ignorer,
    sorting_strategy=AscendingSortStrategy(case_sensitive=False),
    style=TreeStyle(),
    formatter=PlainTextFormatter()
)

# Generate and save the directory structure
structure = generator.generate()
print(structure)
```

### Creating Directory Structure from Template
You can create a directory structure from a template using the `StructureWriter` class. Here is an example:
```python
from dirmapper_core.writer.structure_writer import StructureWriter

# Define the base path where the structure will be created
base_path = 'Path/To/Your/Project'

# Define the structure template
structure_template = {
    'meta': {
        'version': '1.1',
        'author': 'Your Name',
        'description': 'Sample directory structure',
        'creation_date': '2023-10-01',
        'last_modified': '2023-10-01',
        'license': 'MIT'
    },
    'template': {
        'src': [
            {'main.py': ''},
            {'utils': [
                {'helpers.py': ''}
            ]}
        ],
        'tests': [
            {'test_main.py': ''}
        ],
        'README.md': ''
    }
}

# Initialize StructureWriter
writer = StructureWriter(base_path)

# Create the directory structure
writer.create_structure(structure_template)

# Write the structure to OS file system
writer.write_structure()
```

### Writing Directory Structure to Template File
You can write the generated directory structure to a template file using the `write_template` function. Here is an example:
```python
from dirmapper_core.writer.writer import write_template

# Define the structure template
structure_template = {
    'meta': {
        'version': '1.1',
        'author': 'Your Name',
        'description': 'Sample directory structure',
        'creation_date': '2023-10-01',
        'last_modified': '2023-10-01',
        'license': 'MIT'
    },
    'template': {
        'src': [
            {'main.py': ''},
            {'utils': [
                {'helpers.py': ''}
            ]}
        ],
        'tests': [
            {'test_main.py': ''}
        ],
        'README.md': ''
    }
}

# Define the path to the template file
template_path = 'path/to/your/template.json'

# Write the structure to the template file
write_template(template_path, structure_template)
```

### Summarizing Directory Structure
You can summarize the directory structure using the `DirectorySummarizer` class. Here is an example:
```python
from dirmapper_core.ai.summarizer import DirectorySummarizer
from dirmapper_core.formatter.formatter import JSONFormatter
from dirmapper_core.styles.tree_style import TreeStyle

# Define preferences
preferences = {
    "use_local": False,  # Set to False to use API-based summarization
    "api_token": "your_openai_api_token"
}

# Set the format instructions for output
format_instruction = {
                'style': TreeStyle(),
                'length': 10,
                'max_depth': 5  # Pass max depth to the summarizer
                # Add other format instructions here
            }
# Initialize DirectorySummarizer
summarizer = DirectorySummarizer(
    formatter=PlainTextFormatter(),
    format_instruction= format_instruction,
    preferences=preferences
)

# Summarize the directory structure
directory_structure = """
path/to/your/project
├── .git/
├── .github/
│   └── workflows/
│       └── publish.yml
├── LICENSE
├── README.md
├── dirmapper_core/
│   ├── __init__.py
│   ├── ai/
│   │   └── summarizer.py
│   ├── data/
│   ├── formatter/
│   ├── generator/
│   ├── ignore/
│   ├── styles/
│   ├── utils/
│   └── writer/
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_cli_utils.py
    ├── test_directory_structure_generator.py
    ├── test_ignore_list_reader.py
    ├── test_main.py
    └── test_path_ignorer.py
"""

summary = summarizer.summarize(directory_structure)
print(summary)
```

## Configuration
### Ignoring Files and Directories
You can specify files and directories to ignore using the .mapping-ignore file or by providing patterns directly to the PathIgnorer class.

Example `.mapping-ignore` file:
```
# Ignore .git directory
.git/
# Ignore all __pycache__ directories
regex:^.*__pycache__$
# Ignore all .pyc files
regex:^.*\.pyc$
# Ignore all .egg-info directories
regex:^.*\.egg-info$
# Ignore all dist directories
regex:^.*dist$
```

### Custom Styles and Formatters
You can create custom styles and formatters by extending the BaseStyle and Formatter classes, respectively.

### Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub.

### License
This project is licensed under the MIT License. See the LICENSE file for details.