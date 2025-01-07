import unittest
from mrkdwn import MarkdownParser

class TestMarkdownTableParsing(unittest.TestCase):
    def test_table_with_empty_cells(self):
        markdown_text = """# Test Document

|Col1|Col2|Servers|Col4|Col5|Col6|Switches|Col8|Col9|Col10|
|---|---|---|---|---|---|---|---|---|---|
|||ttt|ttt|ttt|ttt|ttt|ttt|ttt|ttt|
|aaa||aaa|aaa|aaa|aaa|aaa|aaa|aaa|aaa|
|Qty||bbb|bbb|bbb|bbb|bbb|bbb|bbb|bbb|
|ccc|ccc|ccc|ccc|ccc|ccc|ccc|ccc|ccc|ccc|
||ddd|ddd|ddd|ddd|ddd|ddd|ddd|ddd|ddd|

Some text after the table.
"""
        parser = MarkdownParser(markdown_text)
        tokens = parser.parse()
        
        # Find table token
        table_token = next(t for t in tokens if t.type == 'table')
        
        # Tests
        self.assertIsNotNone(table_token)
        
        # Test headers
        expected_headers = ['Col1', 'Col2', 'Servers', 'Col4', 'Col5', 'Col6', 'Switches', 'Col8', 'Col9', 'Col10']
        self.assertEqual(table_token.meta['header'], expected_headers)
        
        # Test first row with empty cells
        expected_first_row = ['', '', 'ttt', 'ttt', 'ttt', 'ttt', 'ttt', 'ttt', 'ttt', 'ttt']
        self.assertEqual(table_token.meta['rows'][0], expected_first_row)
        
        # Test second row
        expected_second_row = ['aaa', '', 'aaa', 'aaa', 'aaa', 'aaa', 'aaa', 'aaa', 'aaa', 'aaa']
        self.assertEqual(table_token.meta['rows'][1], expected_second_row)

if __name__ == '__main__':
    unittest.main()