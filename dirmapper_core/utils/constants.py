
from dirmapper_core.formatter.formatter import HTMLFormatter, JSONFormatter, MarkdownFormatter, PlainTextFormatter
from dirmapper_core.styles.flat_list_style import FlatListStyle
from dirmapper_core.styles.indentation_style import IndentationStyle
from dirmapper_core.styles.list_style import ListStyle
from dirmapper_core.styles.tree_style import TreeStyle


STYLE_MAP = {
    'tree': TreeStyle,
    'indentation': IndentationStyle,
    'flat': FlatListStyle,
    'list': ListStyle,
    # 'html': HTMLStyle,
    # 'json': JSONStyle
}

FORMATTER_MAP = {
    'plain': PlainTextFormatter,
    'html': HTMLFormatter,
    'json': JSONFormatter,
    'markdown': MarkdownFormatter
}

EXTENSIONS = {
    'tree': '.txt',
    'indentation': '.txt',
    'flat': '.txt',
    'list': '.txt',
    'markdown': '.md',
    'html': '.html',
    'json': '.json'
}