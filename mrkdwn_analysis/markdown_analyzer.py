# core.py

import re
from collections import defaultdict

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
        return result

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
        return result
