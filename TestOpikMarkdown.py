import requests
from mrkdwn import MarkdownAnalyzer
import tempfile
import os

def test_opik_markdown():
    url = "https://raw.githubusercontent.com/comet-ml/opik/54b5e52e49cb2fabfa324c7e9ffdbe60111723bf/apps/opik-documentation/documentation/docs/production/production_monitoring.md"
    response = requests.get(url)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write(response.text)
        temp_path = f.name

    try:
        analyzer = MarkdownAnalyzer(temp_path)
        code_blocks = analyzer.identify_code_blocks()
        
        for block in code_blocks.get("Code block", []):
            print(f"\nLine {block['start_line']}:")
            print(f"Language: {block['language']}")
            print("Content:")
            print(block['content'])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    test_opik_markdown()