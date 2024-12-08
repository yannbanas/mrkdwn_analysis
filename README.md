# mrkdwn_analysis

`mrkdwn_analysis` is a powerful Python library designed to analyze Markdown files. It provides extensive parsing capabilities to extract and categorize various elements within a Markdown document, including headers, sections, links, images, blockquotes, code blocks, lists, tables, tasks (todos), footnotes, and even embedded HTML. This makes it a versatile tool for data analysis, content generation, or building other tools that work with Markdown.

## Features

- **File Loading**: Load any given Markdown file by providing its file path.

- **Header Detection**: Identify all headers (ATX `#` to `######`, and Setext `===` and `---`) in the document, giving you a quick overview of its structure.

- **Section Identification (Setext)**: Recognize sections defined by a block of text followed by `=` or `-` lines, helping you understand the document’s conceptual divisions.

- **Paragraph Extraction**: Distinguish regular text (paragraphs) from structured elements like headers, lists, or code blocks, making it easy to isolate the body content.

- **Blockquote Identification**: Extract all blockquotes defined by lines starting with `>`.

- **Code Block Extraction**: Detect fenced code blocks delimited by triple backticks (```), optionally retrieve their language, and separate programming code from regular text.

- **List Recognition**: Identify both ordered and unordered lists, including task lists (`- [ ]`, `- [x]`), and understand their structure and hierarchy.

- **Tables (GFM)**: Detect GitHub-Flavored Markdown tables, parse their headers and rows, and separate structured tabular data for further analysis.

- **Links and Images**: Identify text links (`[text](url)`) and images (`![alt](url)`), as well as reference-style links. This is useful for link validation or content analysis.

- **Footnotes**: Extract and handle Markdown footnotes (`[^note1]`), providing a way to process reference notes in the document.

- **HTML Blocks and Inline HTML**: Handle HTML blocks (`<div>...</div>`) as a single element, and detect inline HTML elements (`<span style="...">... </span>`) as a unified component.

- **Front Matter**: If present, extract YAML front matter at the start of the file.

- **Counting Elements**: Count how many occurrences of a certain element type (e.g., how many headers, code blocks, etc.).

- **Textual Statistics**: Count the number of words and characters (excluding whitespace). Get a global summary (`analyse()`) of the document’s composition.

## Installation

Install `mrkdwn_analysis` from PyPI:

```bash
pip install markdown-analysis
```

## Usage

Using `mrkdwn_analysis` is straightforward. Import `MarkdownAnalyzer`, create an instance with your Markdown file path, and then call the various methods to extract the elements you need.

```python
from mrkdwn_analysis import MarkdownAnalyzer

analyzer = MarkdownAnalyzer("path/to/document.md")

headers = analyzer.identify_headers()
paragraphs = analyzer.identify_paragraphs()
links = analyzer.identify_links()
...
```

### Example

Consider `example.md`:

```markdown
---
title: "Python 3.11 Report"
author: "John Doe"
date: "2024-01-15"
---

Python 3.11
===========

A major **Python** release with significant improvements...

### Performance Details

```python
import math
print(math.factorial(10))
```

> *Quote*: "Python 3.11 brings the speed we needed"

<div class="note">
  <p>HTML block example</p>
</div>

This paragraph contains inline HTML: <span style="color:red;">Red text</span>.

- Unordered list:
  - A basic point
  - [ ] A task to do
  - [x] A completed task

1. Ordered list item 1
2. Ordered list item 2
```

After analysis:

```python
analyzer = MarkdownAnalyzer("example.md")

print(analyzer.identify_headers())
# {"Header": [{"line": X, "level": 1, "text": "Python 3.11"}, {"line": Y, "level": 3, "text": "Performance Details"}]}

print(analyzer.identify_paragraphs())
# {"Paragraph": ["A major **Python** release ...", "This paragraph contains inline HTML: ..."]}

print(analyzer.identify_html_blocks())
# [{"line": Z, "content": "<div class=\"note\">\n  <p>HTML block example</p>\n</div>"}]

print(analyzer.identify_html_inline())
# [{"line": W, "html": "<span style=\"color:red;\">Red text</span>"}]

print(analyzer.identify_lists())
# {
#   "Ordered list": [["Ordered list item 1", "Ordered list item 2"]],
#   "Unordered list": [["A basic point", "A task to do [Task]", "A completed task [Task done]"]]
# }

print(analyzer.identify_code_blocks())
# {"Code block": [{"start_line": X, "content": "import math\nprint(math.factorial(10))", "language": "python"}]}

print(analyzer.analyse())
# {
#   'headers': 2,
#   'paragraphs': 2,
#   'blockquotes': 1,
#   'code_blocks': 1,
#   'ordered_lists': 2,
#   'unordered_lists': 3,
#   'tables': 0,
#   'html_blocks': 1,
#   'html_inline_count': 1,
#   'words': 42,
#   'characters': 250
# }
```

### Key Methods

- `__init__(self, file_path)`: Load the Markdown file.
- `identify_headers()`: Returns all headers.
- `identify_sections()`: Returns setext sections.
- `identify_paragraphs()`: Returns paragraphs.
- `identify_blockquotes()`: Returns blockquotes.
- `identify_code_blocks()`: Returns code blocks with content and language.
- `identify_lists()`: Returns both ordered and unordered lists (including tasks).
- `identify_tables()`: Returns any GFM tables.
- `identify_links()`: Returns text and image links.
- `identify_footnotes()`: Returns footnotes used in the document.
- `identify_html_blocks()`: Returns HTML blocks as single tokens.
- `identify_html_inline()`: Returns inline HTML elements.
- `identify_todos()`: Returns task items.
- `count_elements(element_type)`: Counts occurrences of a specific element type.
- `count_words()`: Counts words in the entire document.
- `count_characters()`: Counts non-whitespace characters.
- `analyse()`: Provides a global summary (headers count, paragraphs count, etc.).

### Checking and Validating Links

- `check_links()`: Validates text links to see if they are broken (e.g., non-200 status) and returns a list of broken links.

### Global Analysis Example

```python
analysis = analyzer.analyse()
print(analysis)
# {
#   'headers': X,
#   'paragraphs': Y,
#   'blockquotes': Z,
#   'code_blocks': A,
#   'ordered_lists': B,
#   'unordered_lists': C,
#   'tables': D,
#   'html_blocks': E,
#   'html_inline_count': F,
#   'words': G,
#   'characters': H
# }
```

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for bug reports, feature requests, or code improvements. Your input helps make `mrkdwn_analysis` more robust and versatile.
