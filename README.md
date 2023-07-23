# mrkdwn_analysis

`mrkdwn_analysis` is a Python library designed to analyze Markdown files. With its powerful parsing capabilities, it can extract and categorize various elements within a Markdown document, including headers, sections, links, images, blockquotes, code blocks, and lists. This makes it a valuable tool for anyone looking to parse Markdown content for data analysis, content generation, or for building other tools that utilize Markdown.

## Features

- File Loading: The MarkdownAnalyzer can load any given Markdown file provided through the file path.

- Header Identification: The tool can extract all headers from the markdown file, ranging from H1 to H6 tags. This allows users to have a quick overview of the document's structure.

- Section Identification: The analyzer can recognize different sections of the document. It defines a section as a block of text followed by a line composed solely of = or - characters.

- Paragraph Identification: The tool can distinguish between regular text and other elements such as lists, headers, etc., thereby identifying all the paragraphs present in the document.

- Blockquote Identification: The analyzer can identify and extract all blockquotes in the markdown file.

- Code Block Identification: The tool can extract all code blocks defined in the document, allowing you to separate the programming code from the regular text easily.

- List Identification: The analyzer can identify both ordered and unordered lists in the markdown file, providing information about the hierarchical structure of the points.

- Table Identification: The tool can identify and extract tables from the markdown file, enabling users to separate and analyze tabular data quickly.

- Link Identification and Validation: The analyzer can identify all links present in the markdown file, categorizing them into text and image links. Moreover, it can also verify if these links are valid or broken.

- Todo Identification: The tool is capable of recognizing and extracting todos (tasks or action items) present in the document.

- Element Counting: The analyzer can count the total number of a specific element type in the file. This can help in quantifying the extent of different elements in the document.

- Word Counting: The tool can count the total number of words in the file, providing an estimate of the document's length.

- Character Counting: The analyzer can count the total number of characters (excluding spaces) in the file, giving a detailed measure of the document's size.

## Installation
You can install `mrkdwn_analysis` from PyPI:

```bash
pip install mrkdwn_analysis
```

We hope `mrkdwn_analysis` helps you with all your Markdown analyzing needs!

## Usage
Using `mrkdwn_analysis` is simple. Just import the `MarkdownAnalyzer` class, create an instance with your Markdown file, and you're good to go!

```python
from mrkdwn_analysis import MarkdownAnalyzer

analyzer = MarkdownAnalyzer("path/to/your/markdown.md")

headers = analyzer.identify_headers()
sections = analyzer.identify_sections()
...
```

### Class MarkdownAnalyzer

The `MarkdownAnalyzer` class is designed to analyze Markdown files. It has the ability to extract and categorize various elements of a Markdown document.

### `__init__(self, file_path)`

The constructor of the class. It opens the specified Markdown file and stores its content line by line.

- `file_path`: the path of the Markdown file to analyze.

### `identify_headers(self)`

Analyzes the file and identifies all headers (from h1 to h6). Headers are returned as a dictionary where the key is "Header" and the value is a list of all headers found.

### `identify_sections(self)`

Analyzes the file and identifies all sections. Sections are defined as a block of text followed by a line composed solely of `=` or `-` characters. Sections are returned as a dictionary where the key is "Section" and the value is a list of all sections found.

### `identify_paragraphs(self)`

Analyzes the file and identifies all paragraphs. Paragraphs are defined as a block of text that is not a header, list, blockquote, etc. Paragraphs are returned as a dictionary where the key is "Paragraph" and the value is a list of all paragraphs found.

### `identify_blockquotes(self)`

Analyzes the file and identifies all blockquotes. Blockquotes are defined by a line starting with the `>` character. Blockquotes are returned as a dictionary where the key is "Blockquote" and the value is a list of all blockquotes found.

### `identify_code_blocks(self)`

Analyzes the file and identifies all code blocks. Code blocks are defined by a block of text surrounded by lines containing only the "```" text. Code blocks are returned as a dictionary where the key is "Code block" and the value is a list of all code blocks found.

### `identify_ordered_lists(self)`

Analyzes the file and identifies all ordered lists. Ordered lists are defined by lines starting with a number followed by a dot. Ordered lists are returned as a dictionary where the key is "Ordered list" and the value is a list of all ordered lists found.

### `identify_unordered_lists(self)`

Analyzes the file and identifies all unordered lists. Unordered lists are defined by lines starting with a `-`, `*`, or `+`. Unordered lists are returned as a dictionary where the key is "Unordered list" and the value is a list of all unordered lists found.

### `identify_tables(self)`

Analyzes the file and identifies all tables. Tables are defined by lines containing `|` to delimit cells and are separated by lines containing `-` to define the borders. Tables are returned as a dictionary where the key is "Table" and the value is a list of all tables found.

### `identify_links(self)`

Analyzes the file and identifies all links. Links are defined by the format `[text](url)`. Links are returned as a dictionary where the keys are "Text link" and "Image link" and the values are lists of all links found.

### `check_links(self)`

Checks all links identified by `identify_links` to see if they are broken (return a 404 error). Broken links are returned as a list, each item being a dictionary containing the line number, link text, and URL.

### `identify_todos(self)`

Analyzes the file and identifies all todos. Todos are defined by lines starting with `- [ ] `. Todos are returned as a list, each item being a dictionary containing the line number and todo text.

### `count_elements(self, element_type)`

Counts the total number of a specific element type in the file. The `element_type` should match the name of one of the identification methods (for example, "headers" for `identify_headers`). Returns the total number of elements of this type.

### `count_words(self)`

Counts the total number of words in the file. Returns the word count.

### `count_characters(self)`

Counts the total number of characters (excluding spaces) in the file. Returns the character count.

## Contributions
Contributions are always welcome! If you have a feature request, bug report, or just want to improve the code, feel free to create a pull request or open an issue.
