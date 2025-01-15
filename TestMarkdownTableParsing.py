from mrkdwn import InlineParser, MarkdownAnalyzer, MarkdownParser

class MarkdownAnalyzerString(MarkdownAnalyzer):
    def __init__(self, text, encoding='utf-8'):
        self.text = text
        parser = MarkdownParser(self.text)
        self.tokens = parser.parse()
        self.references = parser.references
        self.footnotes = parser.footnotes
        self.inline_parser = InlineParser(references=self.references, footnotes=self.footnotes)
        self._parse_inline_tokens()

markdown_data = """
|Col1|Col2|Servers|Col4|Col5|Col6|Switches|Col8|Col9|Col10|
|---|---|---|---|---|---|---|---|---|---|
|||ttt|ttt|ttt|ttt|ttt|ttt|ttt|ttt|
|aaa||aaa|aaa|aaa|aaa|aaa|aaa|aaa|aaa|
|Qty||bbb|bbb|bbb|bbb|bbb|bbb|bbb|bbb|
|ccc|ccc|ccc|ccc|ccc|ccc|ccc|ccc|ccc|ccc|
||ddd|ddd|ddd|ddd|ddd|ddd|ddd|ddd|ddd|
"""

analyzer = MarkdownAnalyzerString(markdown_data)
tables = analyzer.identify_tables()
print(tables)