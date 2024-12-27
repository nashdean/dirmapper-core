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
# Example usage

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
    root_dir='./path/to/your/directory',
    output='output.txt',
    ignorer=path_ignorer,
    sorting_strategy=AscendingSortStrategy(case_sensitive=False),
    style=TreeStyle(),
    formatter=PlainTextFormatter()
)

# Generate the directory structure into the style specified when initializing DirectoryStructureGenerator
structure = generator.generate() # Returns str
```
Generating a directory structure results in a formatted string depending on your style and formatter. Here is an example of the `TreeStyle`:
```
/path/to/root/directory
├── .devcontainer
│   ├── devcontainer.json
│   └── Dockerfile
├── .DS_Store
├── .git
├── .gitignore
├── .mapping-ignore
├── game
│   ├── __init__.py
│   ├── colors.py
│   ├── config.py
│   ├── display.py
│   ├── fonts.py
│   ├── game_loop.py
│   ├── obstacles.py
│   ├── score.py
│   └── snake.py
├── high_scores.yaml
├── main.py
├── main.spec
├── README.md
└── requirements.txt
```
See the [styles](dirmapper_core/styles) folder for all valid style examples.

You may also generate a raw DirectoryStructure object if you set the parameter `styled` to False in the `generate()` method. This allows access to the `DirectoryStructure` class helper functions and access to `DirectoryItems`
```python
# ...
structure = generator.generate(styled=False) # Returns DirectoryStructure object

# Access file content lazily
for item in structure.to_list():
    if item.metadata.get('content') is not None:
        print(f"Content of {item.path}: {item.content}")
```

### Creating Directory Structure from Template
You can create a directory structure from a template using the `StructureWriter` class. Here is an example:
```python
from dirmapper_core.writer.structure_writer import StructureWriter

# Define the base path where the structure will be created
base_path = 'Path/To/Your/Project'

# Define the structure template
structure_template = {
    "meta": {
        "version": "2.0",
        "source": "dirmapper",
        "author": "root",
        "root_path": base_path,
        "creation_date": "2024-11-01T20:06:14.510200",
        "last_modified": "2024-11-01T20:06:14.510211"
    },
    "template": {
        "requirements.txt": {},
        "tests/": {
            "test1.py": {},
            "__init__.py": {}
        },
        "docs/": {},
        "README.md": {},
        "setup.py": {},
        ".gitignore": {},
        "src/": {
            "snake_game/": {
                "__init__.py": {},
                "utils/": {
                    "helper.py": {}
                },
                "main.py": {}
            }
        }
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
from dirmapper_core.writer.template_writer import write_template

# Define the path to the template file
template_path = 'path/to/your/template.json'

# Define the structure template
structure_template = {
    "meta": {
        "version": "2.0",
        "source": "dirmapper",
        "author": "root",
        "root_path": template_path,
        "creation_date": "2024-11-01T20:06:14.510200",
        "last_modified": "2024-11-01T20:06:14.510211"
    },
    "template": {
        "requirements.txt": {},
        "tests/": {
            "test1.py": {},
            "__init__.py": {}
        },
        "docs/": {},
        "README.md": {},
        "setup.py": {},
        ".gitignore": {},
        "src/": {
            "snake_game/": {
                "__init__.py": {},
                "utils/": {
                    "helper.py": {}
                },
                "main.py": {}
            }
        }
    }
}

write_template(template_path, structure_template)
```
You may also use a valid styled directory string (i.e. `tree`) as your `structure_template` in the example above to write a YAML or JSON template file.

### Writing a Directory Structure Formatted String to Template
You can create a JSON template from a formatted directory structure string. Here is a valid example using the `tree` style:
```python
import json
from dirmapper_core.writer.template_parser import TemplateParser

tp = TemplateParser()
template = """
/path/to/root/directory
├── .git/
├── .github/
│   └── workflows/
│       ├── check_version.yaml
│       ├── publish.yaml
│       └── update-homebrew-formula.yml
├── .gitignore
├── .pytest_cache/
├── CHANGELOG.md
├── docs/
├── LICENSE
├── Makefile
├── pyproject.toml
├── README.md
├── requirements.txt
├── src/
│   └── dirmapper/
│       ├── __init__.py
│       ├── ai/
│       │   └── summarizer.py
│       ├── api_client.py
│       ├── config.py
│       ├── config_manager.py
│       ├── data/
│       │   └── .mapping-ignore
│       ├── main.py
│       ├── reader/
│       │   ├── __init__.py
│       │   └── reader.py
│       ├── token_manager.py
│       └── writer/
│           ├── __init__.py
│           └── writer.py
└── tests/
    ├── __init__.py
    └── test_main.py
"""
parsed_template = tp.parse_from_directory_structure(template)
print(json.dumps(parsed_template, indent=4))
```
Other allowable styles include `list`, `flat`, and `indentation`.

### Summarizing Directory Structure
You can summarize the directory structure using the `DirectorySummarizer` class. Here is an example:
```python
from dirmapper_core.generator.directory_structure_generator import DirectoryStructureGenerator
from dirmapper_core.ai.summarizer import DirectorySummarizer
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.styles.tree_style import TreeStyle

# Initialize DirectorySummarizer with configuration
config = {
    "use_local": False,
    "api_token": "your_openai_api_token",
    "summarize_file_content": True,  # Enable file content summarization
    "max_file_summary_words": 50     # Limit file summaries to 50 words
}

summarizer = DirectorySummarizer(config)

# Create a DirectoryStructure instance
root_dir = "path/to/root/project"
dsg = DirectoryStructureGenerator("path/to/root/project")
structure = dsg.generate(styled = False)

# Generate summaries
result = summarizer.summarize(structure)
print(json.dumps(result, indent=2))

# Nicely format your short summaries to the terminal
print(TreeStyle.write_structure_with_short_summaries(structure))
```

In the above example, you see that the __*result*__ from the `DirectorySummarizer` is a dict for easy JSON convertability. If you want to view the directory in a *tree* style, you can use the `write_structure_with_short_summaries` method which takes a DirectoryStructure object.

For more details on the `DirectorySummarizer` class, see the [summarizer.py](dirmapper_core/ai/summarizer.py) file. You can also read the [AI Summarizer](dirmapper_core/ai/README.md) documentation for more information.

### Summarizing Files
You can summarize individual files using the `FileSummarizer` class. Here is an example.
```python
from dirmapper_core.ai.summarizer import FileSummarizer

preferences = {
    "use_local": False,
    "api_token": "your_openai_api_token_here"
}

file_summarizer = FileSummarizer(preferences)
file_path = "/path/to/your/file.py"
summary = file_summarizer.summarize_file(file_path, max_words=150)
print("File Summary:")
print(summary)
```

### Paginating Directory Structure
You can paginate a large directory structure into smaller chunks using the `DirectoryPaginator` class. Here is an example:
```python
from dirmapper_core.models.directory_structure import DirectoryStructure
from dirmapper_core.utils.paginator import DirectoryPaginator

# Create a DirectoryStructure instance
structure = DirectoryStructure()

# Add items to the structure
# ... (add items to the structure)

# Initialize DirectoryPaginator
paginator = DirectoryPaginator(max_items_per_page=20)

# Paginate the directory structure
paginated_structures = paginator.paginate(structure)

# Process each paginated structure
for paginated_structure in paginated_structures:
    print(paginated_structure)
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

## Appendix
### Working with DirectoryStructure Class
All styles and many functions work with the DirectoryStructure class under the hood. This class is essentially an abstracted list of DirectoryItem objects. Below is a sample usage of initializing, adding items, and converting to a specialized dictionary object.
```python
# Create a new DirectoryStructure instance
structure = DirectoryStructure()

# Add items to the structure
structure.add_item(DirectoryItem('/path/to/game', 0, 'game', {
    'type': 'directory',
    'content': None,
    'summary': None,
    'short_summary': None,
    'tags': []
}))

structure.add_item(DirectoryItem('/path/to/game/game_loop.py', 1, 'game_loop.py', {
    'type': 'file',
    'content': 'def main_loop():\n    while True:\n        update()\n        render()',
    'summary': None,
    'short_summary': None,
    'tags': []
}))

structure.add_item(DirectoryItem('/path/to/game/snake.py', 1, 'snake.py', {
    'type': 'file',
    'content': 'class Snake:\n    def __init__(self):\n        self.length = 1',
    'summary': None,
    'short_summary': None,
    'tags': []
}))

    # Convert to nested dictionary
    nested_dict = structure.to_nested_dict(use_json_style=False)

    # Print the result in a readable format
    print(json.dumps(nested_dict, indent=2))
```
The above code will generate the following output to the console:
```json
{
  "path": {
    "to": {
      "game": {
        "__keys__": {
          "type": "directory",
          "content": null,
          "summary": null,
          "short_summary": null,
          "tags": []
        },
        "game_loop.py": {
          "__keys__": {
            "type": "file",
            "content": "def main_loop():\n    while True:\n        update()\n        render()",
            "summary": null,
            "short_summary": null,
            "tags": []
          }
        },
        "snake.py": {
          "__keys__": {
            "type": "file",
            "content": "class Snake:\n    def __init__(self):\n        self.length = 1",
            "summary": null,
            "short_summary": null,
            "tags": []
          }
        }
      }
    }
  }
}
```
If you chose to set the parameter `use_json_style` in the method `to_nested_dict` to True, the output would be a JSON-style dict from the [JSONStyle Class](./dirmapper_core/styles/json_style.py).

### Working with DirectoryItem Class
The most basic element of a directory structure is an item represented by the `DirectoryItem` class. This class is an abstracted object representing a `file` or `directory`. Each object holds valuable metadata about the underlying item, including summaries of the contents which can be generated with AI.
```python
    DirectoryItem(
        path='/path/to/project/README.md',
        level=1,
        name='README.md',
        metadata={
            'type': 'file',
            'content': '# Project Documentation',
            'content_hash': 'a1b2c3d4e5f6g7h8i9j0',
            'summary': None,
            'short_summary': None,
            'tags': []
        }
    )
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License
This project is licensed under the MIT License. See the LICENSE file for details.