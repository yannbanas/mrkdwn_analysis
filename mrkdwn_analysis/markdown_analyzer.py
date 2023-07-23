import re
import requests
from collections import defaultdict, Counter

class MarkdownAnalyzer:
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.lines = file.readlines()
            
    def identify_headers(self):
        result = defaultdict(list)
        pattern = r'^(#{1,6})\s(.*)'
        pattern_image = r'!\[.*?\]\((.*?)\)'  # pattern to identify images
        for i, line in enumerate(self.lines):
            line_without_images = re.sub(pattern_image, '', line)  # remove images from the line
            match = re.match(pattern, line_without_images)
            if match:
                cleaned_line = re.sub(r'^#+', '', line_without_images).strip()
                result["Header"].append(cleaned_line)
        return dict(result)  # Convert defaultdict to dict before returning

    def identify_sections(self):
        result = defaultdict(list)
        pattern = r'^.*\n[=-]{2,}$'
        for i, line in enumerate(self.lines):
            if i < len(self.lines) - 1:
                match = re.match(pattern, line + self.lines[i+1])
            else:
                match = None
            if match:
                if self.lines[i+1].strip().startswith("===") or self.lines[i+1].strip().startswith("---"):
                    result["Section"].append(line.strip())
        return dict(result)  # Convert defaultdict to dict before returning
    
    def identify_paragraphs(lines):
        result = defaultdict(list)
        pattern = r'^(?!#)(?!\n)(?!>)(?!-)(?!=)(.*\S)'
        pattern_underline = r'^.*\n[=-]{2,}$'
        in_code_block = False
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
            if in_code_block:
                continue
            if i < len(lines) - 1:
                match_underline = re.match(pattern_underline, line + lines[i+1])
                if match_underline:
                    continue
            match = re.match(pattern, line)
            if match and line.strip() != '```':  # added a condition to skip lines that are just ```
                result["Paragraph"].append(line.strip())
        return dict(result)

    def identify_blockquotes(lines):
        result = defaultdict(list)
        pattern = r'^(>{1,})\s(.*)'
        blockquote = None
        in_code_block = False
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block  # Flip the flag
            if in_code_block:
                continue  # Skip processing for code blocks
            match = re.match(pattern, line)
            if match:
                depth = len(match.group(1))  # depth is determined by the number of '>' characters
                text = match.group(2).strip()
                if depth > 2:
                    raise ValueError(f"Encountered a blockquote of depth {depth} at line {i+1}, but the maximum allowed depth is 2")
                if blockquote is None:
                    # Start of a new blockquote
                    blockquote = text
                else:
                    # Continuation of the current blockquote, regardless of depth
                    blockquote += " " + text
            elif blockquote is not None:
                # End of the current blockquote
                result["Blockquote"].append(blockquote)
                blockquote = None

        if blockquote is not None:
            # End of the last blockquote
            result["Blockquote"].append(blockquote)

        return dict(result)

    def identify_code_blocks(lines):
        result = defaultdict(list)
        pattern = r'^```'
        in_code_block = False
        code_block = None
        for i, line in enumerate(lines):
            match = re.match(pattern, line.strip())
            if match:
                if in_code_block:
                    # End of code block
                    in_code_block = False
                    code_block += "\n" + line.strip()  # Add the line to the code block before ending it
                    result["Code block"].append(code_block)
                    code_block = None
                else:
                    # Start of code block
                    in_code_block = True
                    code_block = line.strip()
            elif in_code_block:
                code_block += "\n" + line.strip()

        if code_block is not None:
            result["Code block"].append(code_block)
        
        return dict(result)

    def identify_ordered_lists(lines):
        result = defaultdict(list)
        pattern = r'^\s*\d+\.\s'
        in_list = False
        list_items = []
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                if not in_list:
                    # Start of a new list
                    in_list = True
                # Add the current line to the current list
                list_items.append(line.strip())
            elif in_list:
                # End of the current list
                in_list = False
                result["Ordered list"].append(list_items)
                list_items = []

        if list_items:
            # End of the last list
            result["Ordered list"].append(list_items)

        return dict(result)

    def identify_unordered_lists(lines):
        result = defaultdict(list)
        pattern = r'^\s*((\d+\\\.|[-*+])\s)'
        in_list = False
        list_items = []
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                if not in_list:
                    # Start of a new list
                    in_list = True
                # Add the current line to the current list
                list_items.append(line.strip())
            elif in_list:
                # End of the current list
                in_list = False
                result["Unordered list"].append(list_items)
                list_items = []

        if list_items:
            # End of the last list
            result["Unordered list"].append(list_items)

        return dict(result)
    
    def identify_tables(self):
        result = defaultdict(list)
        table_pattern = re.compile(r'^ {0,3}\|(?P<table_head>.+)\|[ \t]*\n' +
                                   r' {0,3}\|(?P<table_align> *[-:]+[-| :]*)\|[ \t]*\n' +
                                   r'(?P<table_body>(?: {0,3}\|.*\|[ \t]*(?:\n|$))*)\n*')
        nptable_pattern = re.compile(r'^ {0,3}(?P<nptable_head>\S.*\|.*)\n' +
                                     r' {0,3}(?P<nptable_align>[-:]+ *\|[-| :]*)\n' +
                                     r'(?P<nptable_body>(?:.*\|.*(?:\n|$))*)\n*')
        
        text = "".join(self.lines)
        matches_table = re.findall(table_pattern, text)
        matches_nptable = re.findall(nptable_pattern, text)
        for match in matches_table + matches_nptable:
            result["Table"].append(match)
            
        return dict(result)
    
    def identify_links(self):
        result = defaultdict(list)
        text_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        image_link_pattern = r'!\[([^\]]*)\]\((.*?)\)'
        for i, line in enumerate(self.lines):
            text_links = re.findall(text_link_pattern, line)
            image_links = re.findall(image_link_pattern, line)
            for link in text_links:
                result["Text link"].append({"line": i+1, "text": link[0], "url": link[1]})
            for link in image_links:
                result["Image link"].append({"line": i+1, "alt_text": link[0], "url": link[1]})
        return dict(result)
    
    def check_links(self):
        broken_links = []
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for i, line in enumerate(self.lines):
            links = re.findall(link_pattern, line)
            for link in links:
                try:
                    response = requests.head(link[1], timeout=3)
                    if response.status_code != 200:
                        broken_links.append({'line': i+1, 'text': link[0], 'url': link[1]})
                except (requests.ConnectionError, requests.Timeout):
                    broken_links.append({'line': i+1, 'text': link[0], 'url': link[1]})
        return broken_links

    def identify_todos(self):
        todos = []
        todo_pattern = r'^\-\s\[ \]\s(.*)'
        for i, line in enumerate(self.lines):
            match = re.match(todo_pattern, line)
            if match:
                todos.append({'line': i+1, 'text': match.group(1)})
        return todos
    
    def count_elements(self, element_type):
        identify_func = getattr(self, f'identify_{element_type}', None)
        if not identify_func:
            raise ValueError(f"No method to identify {element_type} found.")
        elements = identify_func()
        return len(elements.get(element_type.capitalize(), []))

    def count_words(self):
        text = " ".join(self.lines)
        words = text.split()
        return len(words)

    def count_characters(self):
        text = " ".join(self.lines)
        # Exclude white spaces
        characters = [char for char in text if not char.isspace()]
        return len(characters)
    
    def get_text_statistics(self):
        statistics = []
        for i, line in enumerate(self.lines):
            words = line.split()
            if words:
                statistics.append({
                    'line': i+1,
                    'word_count': len(words),
                    'char_count': sum(len(word) for word in words),
                    'average_word_length': sum(len(word) for word in words) / len(words),
                })
        return statistics
    
    def get_word_frequency(self):
        word_frequency = Counter()
        for line in self.lines:
            word_frequency.update(line.lower().split())
        return dict(word_frequency.most_common())
    
    def search(self, search_string):
        result = []
        for i, line in enumerate(self.lines):
            if search_string in line:
                element_types = [func for func in dir(self) if func.startswith('identify_')]
                found_in_element = None
                for etype in element_types:
                    element = getattr(self, etype)()
                    for e, content in element.items():
                        if any(search_string in c for c in content):
                            found_in_element = e
                            break
                    if found_in_element:
                        break
                result.append({"line": i+1, "text": line.strip(), "element": found_in_element})
        return result
    
    def analyse(self):
        analysis = {
            'headers': self.count_elements('headers'),
            'sections': self.count_elements('sections'),
            'paragraphs': self.count_elements('paragraphs'),
            'blockquotes': self.count_elements('blockquotes'),
            'code_blocks': self.count_elements('code_blocks'),
            'ordered_lists': self.count_elements('ordered_lists'),
            'unordered_lists': self.count_elements('unordered_lists'),
            'tables': self.count_elements('tables'),
            'words': self.count_words(),
            'characters': self.count_characters(),
        }
        return analysis
