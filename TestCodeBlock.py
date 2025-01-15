import tempfile
import os
from mrkdwn import MarkdownAnalyzer

def test_code_blocks():
    # Test both fenced and indented code blocks
    test_content = """
Here's a fenced code block:
```python
def hello():
    print("Hello")
```

Here's an indented code block:
    def world():
        print("World")
        return True

    for i in range(3):
        world()

Mixed block:
```python
def mixed():
    print("test")
```
    def indented():
        return True
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write(test_content)
        temp_path = f.name

    try:
        analyzer = MarkdownAnalyzer(temp_path)
        code_blocks = analyzer.identify_code_blocks()
        
        print("\nCode Blocks Found:")
        for block in code_blocks.get("Code block", []):
            print(f"\n{'='*50}")
            print(f"Type: {'Fenced' if block['language'] else 'Indented'}")
            print(f"Line: {block['start_line']}")
            print(f"Code Type: {block['meta'].get('code_type', 'fenced')}")
            print(f"Language: {block['language']}")
            print(f"{'='*50}")
            print("Content:")
            print(block['content'])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    test_code_blocks()