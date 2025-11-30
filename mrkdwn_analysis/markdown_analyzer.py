#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module complet pour le parsing, l’analyse et la conversion de documents Markdown,
y compris la transformation intégrale d’un site web en document Markdown structuré.

Ce module intègre également le support MDX et quelques extensions utiles.
"""

import re
import logging
import os
import json
import time
from collections import defaultdict, deque
from urllib.parse import urljoin, urlparse
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Union, Callable, Any

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# UTILITAIRES ET DECORATEURS DE PERFORMANCE
# =============================================================================

def cached_property(func):
    """Decorator for cached properties to improve performance."""
    attr_name = '_cache_' + func.__name__

    @wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)

    return property(wrapper)


def timed_execution(func):
    """Decorator to measure execution time of functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(f"{func.__name__} executed in {elapsed:.4f}s")
        return result
    return wrapper


# =============================================================================
# PARTIE 1 : PARSING ET ANALYSE DU MARKDOWN / MDX
# =============================================================================

class BlockToken:
    def __init__(self, type_, content="", level=None, meta=None, line=None):
        self.type = type_
        self.content = content
        self.level = level
        self.meta = meta or {}
        self.line = line

class InlineParser:
    IMAGE_OR_LINK_RE = re.compile(r'(!?\[([^\]]*)\])(\(([^\)]+)\)|\[([^\]]+)\])')
    CODE_INLINE_RE = re.compile(r'`([^`]+)`')
    EMPHASIS_RE = re.compile(r'(\*\*|__)(.*?)\1|\*(.*?)\*|_(.*?)_')
    FOOTNOTE_RE = re.compile(r'\[\^([^\]]+)\]')
    HTML_INLINE_RE = re.compile(r'<[a-zA-Z/][^>]*>')
    HTML_INLINE_BLOCK_RE = re.compile(r'<([a-zA-Z]+)([^>]*)>(.*?)</\1>', re.DOTALL)

    def __init__(self, references=None, footnotes=None):
        self.references = references or {}
        self.footnotes = footnotes or {}

    def parse_inline(self, text):
        result = {
            "text_links": [],
            "image_links": [],
            "inline_code": [],
            "emphasis": [],
            "footnotes_used": [],
            "html_inline": []
        }

        # Traitement des footnotes
        used_footnotes = set()
        for fm in self.FOOTNOTE_RE.finditer(text):
            fid = fm.group(1)
            if fid in self.footnotes and fid not in used_footnotes:
                used_footnotes.add(fid)
                result["footnotes_used"].append({"id": fid, "content": self.footnotes[fid]})

        # Traitement du code inline
        for cm in self.CODE_INLINE_RE.finditer(text):
            code = cm.group(1)
            result["inline_code"].append(code)

        # Traitement de l'emphase
        for em_match in self.EMPHASIS_RE.finditer(text):
            emphasized_text = em_match.group(2) or em_match.group(3) or em_match.group(4)
            if emphasized_text:
                result["emphasis"].append(emphasized_text)

        # Extraction améliorée du HTML inline grâce à BeautifulSoup
        soup = BeautifulSoup(text, 'html.parser')
        for tag in soup.find_all():
            result["html_inline"].append(str(tag))

        # Extraction des liens et images via regex
        temp_text = text
        for mm in self.IMAGE_OR_LINK_RE.finditer(temp_text):
            prefix = mm.group(1)
            inner_text = mm.group(2)
            url = mm.group(4)
            ref_id = mm.group(5)
            is_image = prefix.startswith('!')
            final_url = url
            if ref_id and ref_id.lower() in self.references:
                final_url = self.references[ref_id.lower()]
            if is_image:
                if final_url:
                    result["image_links"].append({"alt_text": inner_text, "url": final_url})
            else:
                if final_url:
                    result["text_links"].append({"text": inner_text, "url": final_url})
        return result

class MarkdownParser:
    FRONTMATTER_RE = re.compile(r'^---\s*$')
    ATX_HEADER_RE = re.compile(r'^(#{1,6})\s+(.*)$')
    SETEXT_H1_RE = re.compile(r'^=+\s*$')
    SETEXT_H2_RE = re.compile(r'^-+\s*$')
    FENCE_RE = re.compile(r'^```([^`]*)$')
    BLOCKQUOTE_RE = re.compile(r'^(>\s?)(.*)$')
    ORDERED_LIST_RE = re.compile(r'^\s*\d+\.\s+(.*)$')
    UNORDERED_LIST_RE = re.compile(r'^\s*[-+*]\s+(.*)$')
    HR_RE = re.compile(r'^(\*{3,}|-{3,}|_{3,})\s*$')
    TABLE_SEPARATOR_RE = re.compile(r'^\|?(\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$')
    REFERENCE_DEF_RE = re.compile(r'^\[([^\]]+)\]:\s+(.*?)\s*$', re.MULTILINE)
    FOOTNOTE_DEF_RE = re.compile(r'^\[\^([^\]]+)\]:\s+(.*?)\s*$', re.MULTILINE)
    HTML_BLOCK_START = re.compile(r'^(<([a-zA-Z]+)([^>]*)>|<!--)')
    HTML_BLOCK_END_COMMENT = re.compile(r'-->\s*$')

    def __init__(self, text):
        self.lines = text.split('\n')
        self.length = len(self.lines)
        self.pos = 0
        self.tokens = []
        self.text = text
        self.references = {}
        self.footnotes = {}
        self.extract_references_and_footnotes()

    def extract_references_and_footnotes(self):
        for m in self.REFERENCE_DEF_RE.finditer(self.text):
            rid, url = m.groups()
            self.references[rid.lower()] = url
        for m in self.FOOTNOTE_DEF_RE.finditer(self.text):
            fid, content = m.groups()
            self.footnotes[fid] = content

    def parse(self):
        if self.pos < self.length and self.FRONTMATTER_RE.match(self.lines[self.pos].strip()):
            self.parse_frontmatter()
        while self.pos < self.length:
            if self.pos >= self.length:
                break
            line = self.lines[self.pos]
            if not line.strip():
                self.pos += 1
                continue

            # --- Gestion des blocs de code indentés ---
            if line.startswith("    ") or line.startswith("\t"):
                self.parse_indented_code_block()
                continue

            if self.is_table_start():
                self.parse_table()
                continue
            if self.is_html_block_start(line):
                self.parse_html_block()
                continue

            m = self.ATX_HEADER_RE.match(line)
            if m:
                level = len(m.group(1))
                text = m.group(2).strip()
                self.tokens.append(BlockToken('header', content=text, level=level, line=self.pos+1))
                self.pos += 1
                continue

            if self.pos+1 < self.length:
                next_line = self.lines[self.pos+1].strip()
                if self.SETEXT_H1_RE.match(next_line):
                    text = line.strip()
                    self.tokens.append(BlockToken('header', content=text, level=1, line=self.pos+1))
                    self.pos += 2
                    continue
                if self.SETEXT_H2_RE.match(next_line):
                    text = line.strip()
                    self.tokens.append(BlockToken('header', content=text, level=2, line=self.pos+1))
                    self.pos += 2
                    continue

            if self.HR_RE.match(line.strip()):
                self.tokens.append(BlockToken('hr', line=self.pos+1))
                self.pos += 1
                continue

            fm = self.FENCE_RE.match(line.strip())
            if fm:
                lang = fm.group(1).strip()
                self.parse_fenced_code_block(lang)
                continue

            bm = self.BLOCKQUOTE_RE.match(line)
            if bm:
                self.parse_blockquote()
                continue

            om = self.ORDERED_LIST_RE.match(line)
            um = self.UNORDERED_LIST_RE.match(line)
            if om or um:
                self.parse_list(ordered=bool(om))
                continue

            self.parse_paragraph()

        return self.tokens

    def parse_indented_code_block(self):
        """Parse un bloc de code indenté (au moins 4 espaces ou une tabulation)."""
        start = self.pos
        lines = []
        while self.pos < self.length:
            line = self.lines[self.pos]
            if line.startswith("    ") or line.startswith("\t"):
                # Supprimer l'indentation (4 espaces ou 1 tabulation)
                if line.startswith("    "):
                    lines.append(line[4:])
                else:
                    lines.append(line[1:])
                self.pos += 1
            else:
                break
        if lines:
            content = "\n".join(lines)
            self.tokens.append(BlockToken('code', content=content, meta={"language": None, "code_type": "indented"}, line=start+1))

    def get_emojis(self, text):
        """Extrait et retourne la liste des emojis présents dans le texte."""
        emoji_pattern = re.compile("[" 
            u"\U0001F600-\U0001F64F"  # Émoticônes
            u"\U0001F300-\U0001F5FF"  # Symboles & pictogrammes
            u"\U0001F680-\U0001F6FF"  # Symboles de transport & cartes
            u"\U0001F1E0-\U0001F1FF"  # Drapeaux (iOS)
            "]+", flags=re.UNICODE)
        return emoji_pattern.findall(text)
    
    def is_html_block_start(self, line):
        return self.HTML_BLOCK_START.match(line.strip()) is not None

    def parse_html_block(self):
        start = self.pos
        lines = []
        first_line = self.lines[self.pos].strip()
        comment_mode = first_line.startswith('<!--')
        while self.pos < self.length:
            line = self.lines[self.pos]
            lines.append(line)
            self.pos += 1
            if comment_mode and self.HTML_BLOCK_END_COMMENT.search(line):
                break
            else:
                if self.pos < self.length:
                    nxt_line = self.lines[self.pos]
                    if not nxt_line.strip():
                        break
                else:
                    break
        content = "\n".join(lines)
        self.tokens.append(BlockToken('html_block', content=content, line=start+1))

    def starts_new_block_peek(self):
        if self.pos < self.length:
            nxt = self.lines[self.pos].strip()
            return self.starts_new_block(nxt)
        return False

    def is_table_start(self):
        if self.pos+1 < self.length:
            line = self.lines[self.pos].strip()
            next_line = self.lines[self.pos+1].strip()
            if '|' in line and '|' in next_line and self.TABLE_SEPARATOR_RE.match(next_line):
                return True
        return False

    def parse_table(self):
        start = self.pos
        header_line = self.lines[self.pos].strip()
        separator_line = self.lines[self.pos+1].strip()
        self.pos += 2
        rows = []
        while self.pos < self.length:
            line = self.lines[self.pos].strip()
            if not line or self.starts_new_block(line):
                break
            rows.append(line)
            self.pos += 1
        def parse_row(row):
            parts = row.strip().split('|')
            if parts and not parts[0]:
                parts.pop(0)
            if parts and not parts[-1]:
                parts.pop()
            return [p.strip() for p in parts]
        header_cells = parse_row(header_line)
        data_rows = [parse_row(row) for row in rows]
        self.tokens.append(BlockToken('table', meta={"header": header_cells, "rows": data_rows}, line=start+1))

    def starts_new_block(self, line):
        return (self.ATX_HEADER_RE.match(line) or
                self.FRONTMATTER_RE.match(line) or
                self.FENCE_RE.match(line) or
                self.BLOCKQUOTE_RE.match(line) or
                self.ORDERED_LIST_RE.match(line) or
                self.UNORDERED_LIST_RE.match(line) or
                self.HR_RE.match(line) or
                self.SETEXT_H1_RE.match(line) or
                self.SETEXT_H2_RE.match(line) or
                self.HTML_BLOCK_START.match(line))

    def parse_frontmatter(self):
        self.pos += 1
        start = self.pos
        while self.pos < self.length:
            if self.FRONTMATTER_RE.match(self.lines[self.pos].strip()):
                content = "\n".join(self.lines[start:self.pos])
                self.tokens.append(BlockToken('frontmatter', content=content))
                self.pos += 1
                return
            self.pos += 1
        content = "\n".join(self.lines[start:])
        self.tokens.append(BlockToken('frontmatter', content=content))
        self.pos = self.length

    def parse_fenced_code_block(self, lang):
        initial_line = self.pos
        fence_marker = self.lines[self.pos].strip()[:3]
        self.pos += 1
        start = self.pos
        while self.pos < self.length:
            line = self.lines[self.pos]
            if line.strip() == fence_marker:
                content = "\n".join(self.lines[start:self.pos])
                self.tokens.append(BlockToken('code', content=content, meta={"language": lang}, line=start+1))
                self.pos += 1
                return
            self.pos += 1
        self.pos = initial_line
        raise ValueError(f"Unclosed code fence starting at line {initial_line + 1}")

    def parse_blockquote(self):
        start = self.pos
        lines = []
        while self.pos < self.length:
            line = self.lines[self.pos]
            bm = self.BLOCKQUOTE_RE.match(line)
            if bm:
                lines.append(bm.group(2))
                self.pos += 1
            else:
                break
        content = "\n".join(lines)
        self.tokens.append(BlockToken('blockquote', content=content, line=start+1))

    def parse_list(self, ordered):
        start = self.pos
        items = []
        current_item = []
        list_pattern = self.ORDERED_LIST_RE if ordered else self.UNORDERED_LIST_RE
        while self.pos < self.length:
            line = self.lines[self.pos]
            if not line.strip():
                if current_item:
                    items.append("\n".join(current_item).strip())
                    current_item = []
                self.pos += 1
                continue
            if self.starts_new_block(line.strip()) and not (self.ORDERED_LIST_RE.match(line.strip()) or self.UNORDERED_LIST_RE.match(line.strip())):
                break
            lm = list_pattern.match(line)
            if lm:
                if current_item:
                    items.append("\n".join(current_item).strip())
                    current_item = []
                current_item.append(lm.group(1))
                self.pos += 1
            else:
                current_item.append(line.strip())
                self.pos += 1
        if current_item:
            items.append("\n".join(current_item).strip())
        task_re = re.compile(r'^\[( |x)\]\s+(.*)$')
        final_items = []
        for it in items:
            lines = it.split('\n')
            first_line = lines[0].strip()
            m = task_re.match(first_line)
            if m:
                state = m.group(1)
                text = m.group(2)
                task_checked = (state == 'x')
                final_items.append({"text": text, "task_item": True, "checked": task_checked})
            else:
                final_items.append({"text": it, "task_item": False})
        list_type = 'ordered_list' if ordered else 'unordered_list'
        self.tokens.append(BlockToken(list_type, meta={"items": final_items}, line=start+1))

    def parse_paragraph(self):
        start = self.pos
        lines = []
        while self.pos < self.length:
            line = self.lines[self.pos]
            if not line.strip():
                self.pos += 1
                break
            if self.starts_new_block(line.strip()):
                break
            lines.append(line)
            self.pos += 1
        
        # 🔧 FIX ANTI-BOUCLE INFINIE
        if not lines and self.pos < self.length:
            self.pos += 1
        
        content = "\n".join(lines).strip()
        if content:
            self.tokens.append(BlockToken('paragraph', content=content, line=start+1))

class MarkdownAnalyzer:
    def __init__(self, file_path=None, file_text=None, encoding='utf-8', cache_enabled=True):
        """
        Initialize MarkdownAnalyzer with either a file path or markdown text.
        
        Args:
            file_path (str, optional): Path to the markdown file.
            file_text (str, optional): Markdown text content.
            encoding (str): Text encoding (default: 'utf-8').
            cache_enabled (bool): Enable caching (default: True).
            
        Raises:
            ValueError: If neither or both file_path and file_text are provided.
        """
        # Validation: exactly one of file_path or file_text must be provided
        if file_path is None and file_text is None:
            raise ValueError("Either 'file_path' or 'file_text' must be provided")
        if file_path is not None and file_text is not None:
            raise ValueError("Cannot specify both 'file_path' and 'file_text'")
        
        # Read text from file or use provided text
        if file_path is not None:
            with open(file_path, 'r', encoding=encoding) as f:
                self.text = f.read()
        else:
            self.text = file_text
            
        # Parse the markdown text
        parser = MarkdownParser(self.text)
        self.tokens = parser.parse()
        self.references = parser.references
        self.footnotes = parser.footnotes
        self.inline_parser = InlineParser(references=self.references, footnotes=self.footnotes)
        self._parse_inline_tokens()
        self.cache_enabled = cache_enabled
        self._clear_cache()

    def _clear_cache(self):
        """Clear all cached results."""
        self._method_cache = {}

    @classmethod
    def from_url(cls, url, encoding='utf-8', cache_enabled=True):
        """
        Create a MarkdownAnalyzer from a URL.

        Args:
            url (str): The URL to fetch the markdown content from.
            encoding (str): The encoding to use for the content.
            cache_enabled (bool): Enable caching of parsed results.

        Returns:
            MarkdownAnalyzer: An analyzer for the markdown content.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            text = response.text

            parser = MarkdownParser(text)
            tokens = parser.parse()

            analyzer = cls.__new__(cls)
            analyzer.text = text
            analyzer.tokens = tokens
            analyzer.references = parser.references
            analyzer.footnotes = parser.footnotes
            analyzer.inline_parser = InlineParser(references=analyzer.references, footnotes=analyzer.footnotes)
            analyzer._parse_inline_tokens()
            analyzer.cache_enabled = cache_enabled
            analyzer._clear_cache()

            return analyzer
        except requests.RequestException as exc:
            logger.error(f"Error fetching URL {url}: {exc}")
            raise

    @classmethod
    def from_string(cls, markdown_string, encoding='utf-8', cache_enabled=True):
        """
        Create a MarkdownAnalyzer directly from a markdown string.

        Args:
            markdown_string (str): The markdown content as a string.
            encoding (str): The encoding of the string.
            cache_enabled (bool): Enable caching of parsed results.

        Returns:
            MarkdownAnalyzer: An analyzer for the markdown content.
        """
        parser = MarkdownParser(markdown_string)
        tokens = parser.parse()

        analyzer = cls.__new__(cls)
        analyzer.text = markdown_string
        analyzer.tokens = tokens
        analyzer.references = parser.references
        analyzer.footnotes = parser.footnotes
        analyzer.inline_parser = InlineParser(references=analyzer.references, footnotes=analyzer.footnotes)
        analyzer._parse_inline_tokens()
        analyzer.cache_enabled = cache_enabled
        analyzer._clear_cache()

        return analyzer

    def _parse_inline_tokens(self):
        inline_types = ('paragraph', 'header', 'blockquote')
        for token in self.tokens:
            if token.type in inline_types and token.content:
                inline_data = self.inline_parser.parse_inline(token.content)
                token.meta.update(inline_data)

    def identify_headers(self):
        result = defaultdict(list)
        for token in self.tokens:
            if token.type == 'header':
                result["Header"].append({"line": token.line, "level": token.level, "text": token.content})
        return dict(result)

    def identify_paragraphs(self):
        result = defaultdict(list)
        for token in self.tokens:
            if token.type == 'paragraph':
                result["Paragraph"].append(token.content)
        return dict(result)

    def identify_blockquotes(self):
        result = defaultdict(list)
        for token in self.tokens:
            if token.type == 'blockquote':
                result["Blockquote"].append(token.content)
        return dict(result)

    def identify_code_blocks(self):
        result = defaultdict(list)
        for token in self.tokens:
            if token.type == 'code':
                result["Code block"].append({
                    "start_line": token.line,
                    "content": token.content,
                    "language": token.meta.get("language")
                })
        return dict(result)

    def identify_lists(self):
        result = defaultdict(list)
        for token in self.tokens:
            if token.type == 'ordered_list':
                result["Ordered list"].append(token.meta["items"])
            elif token.type == 'unordered_list':
                result["Unordered list"].append(token.meta["items"])
        return dict(result)

    def identify_tables(self):
        result = defaultdict(list)
        for token in self.tokens:
            if token.type == 'table':
                result["Table"].append({
                    "header": token.meta["header"],
                    "rows": token.meta["rows"]
                })
        return dict(result)

    def identify_links(self):
        result = defaultdict(list)
        for token in self.tokens:
            if "text_links" in token.meta:
                for l in token.meta["text_links"]:
                    result["Text link"].append({"line": token.line, "text": l["text"], "url": l["url"]})
            if "image_links" in token.meta:
                for img in token.meta["image_links"]:
                    result["Image link"].append({"line": token.line, "alt_text": img["alt_text"], "url": img["url"]})
        return dict(result)

    def identify_footnotes(self):
        result = []
        seen = set()
        for token in self.tokens:
            if "footnotes_used" in token.meta:
                for fn in token.meta["footnotes_used"]:
                    key = (fn["id"], fn["content"])
                    if key not in seen:
                        seen.add(key)
                        result.append({"line": token.line, "id": fn["id"], "content": fn["content"]})
        return result

    def identify_inline_code(self):
        codes = []
        for token in self.tokens:
            if "inline_code" in token.meta:
                for c in token.meta["inline_code"]:
                    codes.append({"line": token.line, "code": c})
        return codes

    def identify_emphasis(self):
        ems = []
        for token in self.tokens:
            if "emphasis" in token.meta:
                for e in token.meta["emphasis"]:
                    ems.append({"line": token.line, "text": e})
        return ems

    def identify_task_items(self):
        tasks = []
        for token in self.tokens:
            if token.type in ('ordered_list', 'unordered_list'):
                for it in token.meta["items"]:
                    if it.get("task_item"):
                        tasks.append({
                            "line": token.line,
                            "text": it["text"],
                            "checked": it["checked"]
                        })
        return tasks

    def identify_html_blocks(self):
        result = []
        for token in self.tokens:
            if token.type == 'html_block':
                result.append({"line": token.line, "content": token.content})
        return result

    def identify_html_inline(self):
        result = []
        inline_types = ('paragraph', 'header', 'blockquote')
        for token in self.tokens:
            if token.type in inline_types and "html_inline" in token.meta:
                for h in token.meta["html_inline"]:
                    result.append({"line": token.line, "html": h})
        return result

    def get_tokens_sequential(self):
        """
        Retourne une liste séquentielle de tous les éléments trouvés dans le document markdown,
        chacun avec un identifiant, un type et un contenu.
        
        Returns:
            list: Liste d'éléments au format [{'id': n, 'type': '...', 'content': '...'}]
        """
        result = []
        token_id = 1
        
        for token in self.tokens:
            # Ajouter le token principal
            token_type = token.type
            
            # Convertir certains types pour plus de clarté
            if token_type == 'header':
                token_type = f'header{token.level}'
            
            # Ajouter le token principal à la liste de résultats
            result.append({
                'id': token_id,
                'type': token_type,
                'content': token.content
            })
            token_id += 1
            
            # Traiter les éléments inline si disponibles
            if token.type in ('paragraph', 'header', 'blockquote'):
                # Extraire et traiter les formats inline
                if "emphasis" in token.meta:
                    for emphasis in token.meta["emphasis"]:
                        result.append({
                            'id': token_id,
                            'type': 'italic',
                            'content': emphasis
                        })
                        token_id += 1
                
                if "inline_code" in token.meta:
                    for code in token.meta["inline_code"]:
                        result.append({
                            'id': token_id,
                            'type': 'inline_code',
                            'content': code
                        })
                        token_id += 1
                
                if "text_links" in token.meta:
                    for link in token.meta["text_links"]:
                        result.append({
                            'id': token_id,
                            'type': 'link',
                            'content': link["text"],
                            'url': link["url"]
                        })
                        token_id += 1
                
                if "image_links" in token.meta:
                    for img in token.meta["image_links"]:
                        result.append({
                            'id': token_id,
                            'type': 'image',
                            'content': img["alt_text"],
                            'url': img["url"]
                        })
                        token_id += 1
            
            # Traiter les listes
            if token.type in ('ordered_list', 'unordered_list'):
                for item in token.meta["items"]:
                    item_type = 'list_item'
                    if item.get("task_item"):
                        item_type = 'task_item'
                    
                    result.append({
                        'id': token_id,
                        'type': item_type,
                        'content': item["text"],
                        'checked': item.get("checked", False) if item_type == 'task_item' else None
                    })
                    token_id += 1
        
        return result

    def count_words(self):
        words = self.text.split()
        return len(words)

    def count_characters(self):
        characters = [char for char in self.text if not char.isspace()]
        return len(characters)

    def analyse(self):
        headers = self.identify_headers().get("Header", [])
        paragraphs = self.identify_paragraphs().get("Paragraph", [])
        blockquotes = self.identify_blockquotes().get("Blockquote", [])
        code_blocks = self.identify_code_blocks().get("Code block", [])
        lists = self.identify_lists()
        ordered_lists = lists.get("Ordered list", [])
        unordered_lists = lists.get("Unordered list", [])
        tables = self.identify_tables().get("Table", [])
        html_blocks = self.identify_html_blocks()
        html_inline = self.identify_html_inline()
        analysis = {
            'headers': len(headers),
            'paragraphs': len(paragraphs),
            'blockquotes': len(blockquotes),
            'code_blocks': len(code_blocks),
            'ordered_lists': sum(len(l) for l in ordered_lists),
            'unordered_lists': sum(len(l) for l in unordered_lists),
            'tables': len(tables),
            'html_blocks': len(html_blocks),
            'html_inline_count': len(html_inline),
            'words': self.count_words(),
            'characters': self.count_characters()
        }
        return analysis

    # =============================================================================
    # NOUVELLES FONCTIONNALITÉS - RECHERCHE ET FILTRAGE
    # =============================================================================

    def search_content(self, pattern: str, case_sensitive: bool = False, regex: bool = False) -> List[Dict]:
        """
        Search for content across all elements.

        Args:
            pattern: Search pattern (string or regex)
            case_sensitive: Whether search should be case sensitive
            regex: Whether pattern is a regex

        Returns:
            List of matching elements with context
        """
        flags = 0 if case_sensitive else re.IGNORECASE
        search_re = re.compile(pattern, flags) if regex else re.compile(re.escape(pattern), flags)

        results = []
        for token in self.tokens:
            if token.content and search_re.search(token.content):
                results.append({
                    'type': token.type,
                    'line': token.line,
                    'content': token.content,
                    'level': token.level if hasattr(token, 'level') else None
                })

        return results

    def filter_by_type(self, element_type: str) -> List[BlockToken]:
        """
        Filter tokens by type.

        Args:
            element_type: Type of element to filter (e.g., 'header', 'paragraph', 'code')

        Returns:
            List of matching tokens
        """
        return [token for token in self.tokens if token.type == element_type]

    def find_headers_by_level(self, level: int) -> List[Dict]:
        """
        Find all headers of a specific level.

        Args:
            level: Header level (1-6)

        Returns:
            List of headers at the specified level
        """
        all_headers = self.identify_headers().get("Header", [])
        return [h for h in all_headers if h['level'] == level]

    def get_table_of_contents(self, max_level: int = 6) -> List[Dict]:
        """
        Generate a table of contents from headers.

        Args:
            max_level: Maximum header level to include

        Returns:
            List of TOC entries with hierarchy
        """
        headers = self.identify_headers().get("Header", [])
        toc = []
        for header in headers:
            if header['level'] <= max_level:
                toc.append({
                    'level': header['level'],
                    'text': header['text'],
                    'line': header['line'],
                    'indent': '  ' * (header['level'] - 1)
                })
        return toc

    # =============================================================================
    # EXPORT VERS DIFFÉRENTS FORMATS
    # =============================================================================

    def export_to_json(self, include_metadata: bool = True) -> str:
        """
        Export complete analysis to JSON format.

        Args:
            include_metadata: Include metadata like line numbers

        Returns:
            JSON string representation
        """
        export_data = {
            'summary': self.analyse(),
            'headers': self.identify_headers(),
            'paragraphs': self.identify_paragraphs(),
            'code_blocks': self.identify_code_blocks(),
            'lists': self.identify_lists(),
            'tables': self.identify_tables(),
            'links': self.identify_links(),
            'blockquotes': self.identify_blockquotes()
        }

        if include_metadata:
            export_data['metadata'] = {
                'total_lines': len(self.text.split('\n')),
                'references_count': len(self.references),
                'footnotes_count': len(self.footnotes)
            }

        return json.dumps(export_data, indent=2, ensure_ascii=False)

    def export_to_html(self, include_style: bool = True) -> str:
        """
        Export markdown content to HTML.

        Args:
            include_style: Include basic CSS styling

        Returns:
            HTML string
        """
        html_parts = []

        if include_style:
            html_parts.append("""
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                       max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
                code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
                pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
                blockquote { border-left: 4px solid #ddd; margin: 0; padding-left: 20px; color: #666; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f4f4f4; }
            </style>
            """)

        for token in self.tokens:
            if token.type == 'header':
                html_parts.append(f'<h{token.level}>{token.content}</h{token.level}>')
            elif token.type == 'paragraph':
                html_parts.append(f'<p>{token.content}</p>')
            elif token.type == 'code':
                lang = token.meta.get('language', '')
                html_parts.append(f'<pre><code class="language-{lang}">{token.content}</code></pre>')
            elif token.type == 'blockquote':
                html_parts.append(f'<blockquote>{token.content}</blockquote>')
            elif token.type == 'table':
                html_parts.append(self._table_to_html(token.meta))

        return '\n'.join(html_parts)

    def _table_to_html(self, table_meta: Dict) -> str:
        """Convert table metadata to HTML."""
        html = ['<table>']
        html.append('<thead><tr>')
        for cell in table_meta['header']:
            html.append(f'<th>{cell}</th>')
        html.append('</tr></thead>')
        html.append('<tbody>')
        for row in table_meta['rows']:
            html.append('<tr>')
            for cell in row:
                html.append(f'<td>{cell}</td>')
            html.append('</tr>')
        html.append('</tbody></table>')
        return ''.join(html)

    def export_to_plain_text(self, strip_formatting: bool = True) -> str:
        """
        Export to plain text, optionally stripping markdown formatting.

        Args:
            strip_formatting: Remove markdown syntax

        Returns:
            Plain text content
        """
        if not strip_formatting:
            return self.text

        plain_parts = []
        for token in self.tokens:
            if token.content:
                # Remove markdown formatting
                text = token.content
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
                text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
                text = re.sub(r'`(.+?)`', r'\1', text)  # Inline code
                text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Links
                plain_parts.append(text)

        return '\n\n'.join(plain_parts)

    # =============================================================================
    # STATISTIQUES AVANCÉES
    # =============================================================================

    def get_reading_time(self, words_per_minute: int = 200) -> Dict:
        """
        Calculate estimated reading time.

        Args:
            words_per_minute: Average reading speed

        Returns:
            Dictionary with reading time estimates
        """
        word_count = self.count_words()
        minutes = word_count / words_per_minute

        return {
            'words': word_count,
            'minutes': round(minutes, 1),
            'formatted': f"{int(minutes)} min read" if minutes >= 1 else "< 1 min read"
        }

    def get_complexity_metrics(self) -> Dict:
        """
        Calculate document complexity metrics.

        Returns:
            Dictionary with complexity indicators
        """
        words = self.count_words()
        chars = self.count_characters()
        sentences = len(re.findall(r'[.!?]+', self.text))
        paragraphs = len(self.identify_paragraphs().get("Paragraph", []))

        avg_word_length = chars / words if words > 0 else 0
        avg_sentence_length = words / sentences if sentences > 0 else 0

        return {
            'total_words': words,
            'total_sentences': sentences,
            'total_paragraphs': paragraphs,
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'complexity_score': round((avg_word_length + avg_sentence_length) / 2, 2)
        }

    def get_link_statistics(self) -> Dict:
        """
        Get detailed statistics about links in the document.

        Returns:
            Dictionary with link statistics
        """
        links = self.identify_links()
        text_links = links.get("Text link", [])
        image_links = links.get("Image link", [])

        external_links = []
        internal_links = []

        for link in text_links:
            url = link['url']
            if url.startswith(('http://', 'https://')):
                external_links.append(url)
            else:
                internal_links.append(url)

        return {
            'total_links': len(text_links),
            'total_images': len(image_links),
            'external_links': len(external_links),
            'internal_links': len(internal_links),
            'unique_domains': len(set(urlparse(url).netloc for url in external_links if urlparse(url).netloc))
        }

    # =============================================================================
    # VALIDATION ET VÉRIFICATION AMÉLIORÉES
    # =============================================================================

    def check_links(self, timeout: int = 5, max_workers: int = 10, follow_redirects: bool = True) -> List[Dict]:
        """
        Check all links in the document with parallel execution for better performance.

        Args:
            timeout: Request timeout in seconds
            max_workers: Maximum number of concurrent requests
            follow_redirects: Whether to follow redirects

        Returns:
            List of broken/invalid links
        """
        links = self.identify_links().get("Text link", [])
        broken_links = []

        def check_single_link(link_info):
            url = link_info['url']
            # Skip non-http links
            if not url.startswith(('http://', 'https://')):
                return None

            try:
                response = requests.head(url, timeout=timeout, allow_redirects=follow_redirects)
                # Some servers don't respond to HEAD, try GET
                if response.status_code == 405:
                    response = requests.get(url, timeout=timeout, allow_redirects=follow_redirects, stream=True)

                if response.status_code >= 400:
                    return {
                        'url': url,
                        'line': link_info['line'],
                        'status_code': response.status_code,
                        'text': link_info['text']
                    }
            except requests.RequestException as e:
                return {
                    'url': url,
                    'line': link_info['line'],
                    'error': str(e),
                    'text': link_info['text']
                }

            return None

        # Use ThreadPoolExecutor for parallel link checking
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_link = {executor.submit(check_single_link, link): link for link in links}

            for future in as_completed(future_to_link):
                result = future.result()
                if result:
                    broken_links.append(result)

        return broken_links

    def validate_structure(self) -> Dict:
        """
        Validate document structure and return potential issues.

        Returns:
            Dictionary with validation results
        """
        issues = []
        headers = self.identify_headers().get("Header", [])

        # Check for missing H1
        h1_count = sum(1 for h in headers if h['level'] == 1)
        if h1_count == 0:
            issues.append({'type': 'warning', 'message': 'No H1 header found'})
        elif h1_count > 1:
            issues.append({'type': 'warning', 'message': f'Multiple H1 headers found ({h1_count})'})

        # Check for header level skipping
        for i in range(1, len(headers)):
            prev_level = headers[i-1]['level']
            curr_level = headers[i]['level']
            if curr_level > prev_level + 1:
                issues.append({
                    'type': 'warning',
                    'message': f'Header level skip from H{prev_level} to H{curr_level} at line {headers[i]["line"]}'
                })

        # Check for empty links
        links = self.identify_links()
        for link in links.get("Text link", []):
            if not link['url'] or link['url'].strip() == '':
                issues.append({
                    'type': 'error',
                    'message': f'Empty link at line {link["line"]}'
                })

        return {
            'valid': len([i for i in issues if i['type'] == 'error']) == 0,
            'issues': issues,
            'score': max(0, 100 - (len(issues) * 10))
        }

    # =============================================================================
    # MÉTHODES UTILITAIRES SUPPLÉMENTAIRES
    # =============================================================================

    def get_word_frequency(self, top_n: int = 20, min_word_length: int = 4) -> List[tuple]:
        """
        Get most frequent words in the document.

        Args:
            top_n: Number of top words to return
            min_word_length: Minimum word length to consider

        Returns:
            List of (word, frequency) tuples
        """
        words = re.findall(r'\b\w+\b', self.text.lower())
        words = [w for w in words if len(w) >= min_word_length]

        from collections import Counter
        word_freq = Counter(words)

        return word_freq.most_common(top_n)

    def extract_code_by_language(self, language: str) -> List[Dict]:
        """
        Extract all code blocks of a specific language.

        Args:
            language: Programming language to filter

        Returns:
            List of matching code blocks
        """
        code_blocks = self.identify_code_blocks().get("Code block", [])
        return [cb for cb in code_blocks if cb['language'] == language]

# --- MDX Parsing ---

class MDXMarkdownParser(MarkdownParser):
    JSX_IMPORT_RE = re.compile(r'^import\s+.*?\s+from\s+["\'](.*?)["\'];?\s*$')
    JSX_COMPONENT_START_RE = re.compile(r'^<([A-Z][A-Za-z0-9]*|[a-z]+\.[A-Z][A-Za-z0-9]*).*?(?:>|\/>)$')
    JSX_COMPONENT_END_RE = re.compile(r'^</([A-Z][A-Za-z0-9]*|[a-z]+\.[A-Z][A-Za-z0-9]*)>$')

    def __init__(self, text):
        super().__init__(text)
        self.in_jsx_block = False
        self.current_jsx_content = []
        self.jsx_start_line = None

    def handle_potential_hanging(self):
        if self.pos >= self.length:
            return False
        line = self.lines[self.pos].strip()
        if '</TabItem>' in line or '</Tabs>' in line:
            self.pos += 1
            return True
        return False

    def parse_fenced_code_block(self, lang):
        initial_line = self.pos
        self.pos += 1
        content = []
        while self.pos < self.length:
            line = self.lines[self.pos]
            if line.strip() == '```':
                if content:
                    base_indent = min(len(line) - len(line.lstrip()) for line in content if line.strip())
                    clean_content = []
                    for line in content:
                        if line.strip():
                            clean_content.append('    ' + line[base_indent:])
                    self.tokens.append(BlockToken('code', content='\n'.join(clean_content),
                                                    meta={"language": lang.strip(), "code_type": "fenced"},
                                                    line=initial_line + 1))
                self.pos += 1
                return
            content.append(line)
            self.pos += 1

    def parse(self):
        self.tokens = []
        while self.pos < self.length:
            line = self.lines[self.pos].strip()
            if self.FENCE_RE.match(line):
                lang = self.FENCE_RE.match(line).group(1)
                self.parse_fenced_code_block(lang)
                continue
            self.pos += 1
        return self.tokens

class MDXMarkdownAnalyzer(MarkdownAnalyzer):
    def __init__(self, file_path, encoding='utf-8'):
        with open(file_path, 'r', encoding=encoding) as f:
            self.text = f.read()
        parser = MDXMarkdownParser(self.text)
        self.tokens = parser.parse()
        self.references = parser.references
        self.footnotes = parser.footnotes
        self.inline_parser = InlineParser(references=self.references, footnotes=self.footnotes)
        self._parse_inline_tokens()

# =============================================================================
# PARTIE 2 : CONVERSION D'UN SITE WEB EN DOCUMENT MARKDOWN STRUCTURÉ
# =============================================================================

class WebsiteScraper:
    """
    Classe responsable de l'extraction des pages d'un site web à partir d'une URL de base.
    Le crawling est limité aux pages du même domaine.
    """
    def __init__(self, base_url: str, max_depth: int = 2, timeout: int = 10):
        self.base_url = base_url
        self.max_depth = max_depth
        self.timeout = timeout
        self.visited = set()
        self.domain = urlparse(base_url).netloc

    def scrape(self) -> dict:
        """
        Crawl le site et retourne un dictionnaire {url: html_content}.
        """
        pages = {}
        queue = deque([(self.base_url, 0)])
        while queue:
            current_url, depth = queue.popleft()
            if current_url in self.visited:
                continue
            if depth > self.max_depth:
                continue
            logger.info("Scraping %s (depth %d)", current_url, depth)
            try:
                response = requests.get(current_url, timeout=self.timeout)
                response.raise_for_status()
            except requests.RequestException as exc:
                logger.error("Erreur lors du téléchargement de %s: %s", current_url, exc)
                continue
            html_content = response.text
            pages[current_url] = html_content
            self.visited.add(current_url)
            soup = BeautifulSoup(html_content, "html.parser")
            for link_tag in soup.find_all("a", href=True):
                href = link_tag.get("href")
                next_url = urljoin(current_url, href)
                if self._is_valid_url(next_url):
                    queue.append((next_url, depth + 1))
        return pages

    def _is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.netloc != self.domain:
            return False
        if re.fullmatch(r"#.*", parsed.path):
            return False
        return True

class MarkdownConverter:
    """
    Classe chargée de convertir du contenu HTML en Markdown.
    Utilise la librairie markdownify.
    """
    def __init__(self, heading_style: str = "ATX"):
        self.heading_style = heading_style

    def convert(self, html: str) -> str:
        markdown = md(html, heading_style=self.heading_style)
        return markdown

class WebsiteMarkdownDocument:
    """
    Classe de haut niveau qui transforme un site web en un document Markdown structuré.
    Elle orchestre le crawling (via WebsiteScraper) et la conversion (via MarkdownConverter).
    """
    def __init__(self, base_url: str, max_depth: int = 2):
        self.base_url = base_url
        self.max_depth = max_depth
        self.scraper = WebsiteScraper(base_url, max_depth)
        self.converter = MarkdownConverter()
        self.pages = {}  # Dictionnaire {url: markdown_content}

    def generate(self) -> str:
        html_pages = self.scraper.scrape()
        logger.info("Conversion de %d pages en Markdown", len(html_pages))
        for url, html in html_pages.items():
            markdown_content = self.converter.convert(html)
            self.pages[url] = markdown_content

        # Génération d'un index avec des liens vers chaque page
        document_lines = ["# Index du site\n"]
        for url in sorted(self.pages.keys()):
            title = self._extract_title(self.pages[url])
            anchor = self._url_to_anchor(url)
            document_lines.append(f"- [{title}]({anchor})  <!-- {url} -->")
        document_lines.append("\n---\n")
        for url, markdown in self.pages.items():
            title = self._extract_title(markdown)
            anchor = self._url_to_anchor(url)
            document_lines.append(f"\n## {title}\n")
            document_lines.append(f"<!-- URL: {url} -->\n")
            document_lines.append(markdown)
            document_lines.append("\n---\n")
        return "\n".join(document_lines)

    @staticmethod
    def _extract_title(markdown_text: str) -> str:
        for line in markdown_text.splitlines():
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("# ").strip()
        return "Sans titre"

    @staticmethod
    def _url_to_anchor(url: str) -> str:
        path = urlparse(url).path
        anchor = path.strip("/").replace("/", "-")
        if not anchor:
            anchor = "index"
        return f"#{anchor}"

class MarkdownSiteConverter:
    """
    Classe d'abstraction pour convertir un site web en Markdown.
    Fournit une interface simple et ergonomique.
    """
    def __init__(self, base_url: str, max_depth: int = 2):
        self.document = WebsiteMarkdownDocument(base_url, max_depth)

    def convert_site_to_markdown(self, output_file: str = None) -> str:
        markdown_doc = self.document.generate()
        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(markdown_doc)
                logger.info("Document Markdown écrit dans %s", output_file)
            except IOError as exc:
                logger.error("Erreur d'écriture dans le fichier %s: %s", output_file, exc)
        return markdown_doc

# =============================================================================
# PARTIE 3 : ABSTRACTION POUR UN DOCUMENT MARKDOWN
# =============================================================================

class MarkdownDocument:
    """
    Classe d'abstraction pour un document Markdown.
    Elle encapsule l'analyse et fournit des méthodes simples pour accéder aux informations.

    Cette classe est maintenant enrichie avec des fonctionnalités avancées pour une meilleure
    performance et polyvalence, tout en maintenant la rétrocompatibilité.
    """
    def __init__(self, source, from_url=False, from_string=False, encoding='utf-8', cache_enabled=True):
        """
        Initialize a Markdown document from different sources.

        Args:
            source (str): Either a file path, URL, or markdown string based on the flags.
            from_url (bool): If True, treat source as a URL.
            from_string (bool): If True, treat source as a markdown string directly.
            encoding (str): Text encoding to use.
            cache_enabled (bool): Enable caching for better performance.
        """
        if from_url:
            self.analyzer = MarkdownAnalyzer.from_url(source, encoding=encoding, cache_enabled=cache_enabled)
        elif from_string:
            self.analyzer = MarkdownAnalyzer.from_string(source, encoding=encoding, cache_enabled=cache_enabled)
        else:
            try:
                # Try to open source as a file
                with open(source, 'r', encoding=encoding) as f:
                    text = f.read()
                self.analyzer = MarkdownAnalyzer.from_string(text, encoding=encoding, cache_enabled=cache_enabled)
            except (FileNotFoundError, IOError):
                # Fall back to treating source as raw text
                logger.warning("Source not found as file, treating as string.")
                self.analyzer = MarkdownAnalyzer.from_string(source, encoding=encoding, cache_enabled=cache_enabled)
    
    @classmethod
    def from_file(cls, file_path, encoding='utf-8'):
        """
        Create a MarkdownDocument from a file.
        
        Args:
            file_path (str): Path to the markdown file.
            encoding (str): File encoding.
            
        Returns:
            MarkdownDocument: A document analyzer for the file.
        """
        return cls(file_path, encoding=encoding)
    
    @classmethod
    def from_url(cls, url, encoding='utf-8'):
        """
        Create a MarkdownDocument from a URL.
        
        Args:
            url (str): URL to fetch markdown content from.
            encoding (str): Content encoding.
            
        Returns:
            MarkdownDocument: A document analyzer for the URL content.
        """
        return cls(url, from_url=True, encoding=encoding)
    
    @classmethod
    def from_string(cls, markdown_string, encoding='utf-8'):
        """
        Create a MarkdownDocument directly from a markdown string.
        
        Args:
            markdown_string (str): Markdown content as a string.
            encoding (str): String encoding.
            
        Returns:
            MarkdownDocument: A document analyzer for the string.
        """
        return cls(markdown_string, from_string=True, encoding=encoding)

    # Rest of the methods remain the same
    def get_summary(self):
        return self.analyzer.analyse()

    def get_headers(self):
        return self.analyzer.identify_headers().get("Header", [])

    def get_paragraphs(self):
        return self.analyzer.identify_paragraphs().get("Paragraph", [])

    def get_links(self):
        return self.analyzer.identify_links()

    def get_code_blocks(self):
        return self.analyzer.identify_code_blocks().get("Code block", [])
    
    def get_sequential_elements(self):
        """
        Retourne une liste séquentielle de tous les éléments trouvés dans le document markdown.

        Returns:
            list: Liste d'éléments avec id, type et contenu.
        """
        return self.analyzer.get_tokens_sequential()

    # =============================================================================
    # NOUVELLES MÉTHODES - RECHERCHE ET FILTRAGE
    # =============================================================================

    def search(self, pattern: str, case_sensitive: bool = False, regex: bool = False) -> List[Dict]:
        """
        Search for content in the document.

        Args:
            pattern: Search pattern
            case_sensitive: Case sensitive search
            regex: Use regex pattern

        Returns:
            List of matching elements
        """
        return self.analyzer.search_content(pattern, case_sensitive, regex)

    def find_headers_by_level(self, level: int) -> List[Dict]:
        """Find all headers of a specific level."""
        return self.analyzer.find_headers_by_level(level)

    def get_table_of_contents(self, max_level: int = 6) -> List[Dict]:
        """Generate table of contents."""
        return self.analyzer.get_table_of_contents(max_level)

    # =============================================================================
    # EXPORT VERS DIFFÉRENTS FORMATS
    # =============================================================================

    def to_json(self, include_metadata: bool = True) -> str:
        """Export document analysis to JSON."""
        return self.analyzer.export_to_json(include_metadata)

    def to_html(self, include_style: bool = True) -> str:
        """Export document to HTML."""
        return self.analyzer.export_to_html(include_style)

    def to_plain_text(self, strip_formatting: bool = True) -> str:
        """Export to plain text."""
        return self.analyzer.export_to_plain_text(strip_formatting)

    # =============================================================================
    # STATISTIQUES AVANCÉES
    # =============================================================================

    def get_reading_time(self, words_per_minute: int = 200) -> Dict:
        """Calculate estimated reading time."""
        return self.analyzer.get_reading_time(words_per_minute)

    def get_complexity_metrics(self) -> Dict:
        """Get document complexity metrics."""
        return self.analyzer.get_complexity_metrics()

    def get_link_statistics(self) -> Dict:
        """Get detailed link statistics."""
        return self.analyzer.get_link_statistics()

    def get_word_frequency(self, top_n: int = 20, min_word_length: int = 4) -> List[tuple]:
        """Get most frequent words."""
        return self.analyzer.get_word_frequency(top_n, min_word_length)

    # =============================================================================
    # VALIDATION ET VÉRIFICATION
    # =============================================================================

    def check_links(self, timeout: int = 5, max_workers: int = 10) -> List[Dict]:
        """
        Check all links in parallel for broken links.

        Args:
            timeout: Request timeout
            max_workers: Number of parallel workers

        Returns:
            List of broken links
        """
        return self.analyzer.check_links(timeout, max_workers)

    def validate_structure(self) -> Dict:
        """Validate document structure."""
        return self.analyzer.validate_structure()

    def extract_code_by_language(self, language: str) -> List[Dict]:
        """Extract code blocks by programming language."""
        return self.analyzer.extract_code_by_language(language)

# =============================================================================
# EXEMPLES D'UTILISATION
# =============================================================================

def main():
    markdown_file = "arangodb.md"  # Fichier contenant le markdown fourni dans votre exemple

    try:
        # Création de l'objet MarkdownDocument qui encapsule l'analyse du document
        doc = MarkdownDocument(markdown_file, from_url=False)
    except Exception as e:
        logger.error("Erreur lors du chargement du document Markdown : %s", e)
        return

    # Récupération du résumé de l'analyse
    summary = doc.get_summary()
    print("=== Résumé de l'analyse ===")
    print(json.dumps(summary, indent=4, ensure_ascii=False))

    # Extraction et affichage des en-têtes
    headers = doc.get_headers()
    print("\n=== En-têtes détectés ===")
    for header in headers:
        print(f"Ligne {header['line']}: {header['text']} (Niveau {header['level']})")

    # Affichage des trois premiers paragraphes (pour avoir un aperçu du contenu)
    paragraphs = doc.get_paragraphs()
    print("\n=== Exemples de paragraphes ===")
    for i, para in enumerate(paragraphs[:3], 1):
        print(f"\nParagraphe {i} :\n{para}")

    # Extraction des liens (textuels et images)
    links = doc.get_links()
    print("\n=== Liens extraits ===")
    print(json.dumps(links, indent=4, ensure_ascii=False))

    # Exemple d'export de l'analyse complète en JSON
    analysis_output = {
        "summary": summary,
        "headers": headers,
        "paragraphs": paragraphs,
        "links": links,
        # Vous pouvez ajouter d'autres parties de l'analyse (code_blocks, listes, etc.)
    }
    output_json_file = "analysis_output.json"
    try:
        with open(output_json_file, "w", encoding="utf-8") as f:
            json.dump(analysis_output, f, indent=4, ensure_ascii=False)
        logger.info("Analyse exportée vers %s", output_json_file)
    except Exception as e:
        logger.error("Erreur lors de l'écriture du fichier JSON : %s", e)

    # Obtenir et afficher les éléments séquentiels
    sequential_elements = doc.get_sequential_elements()
    print("\n=== Éléments séquentiels ===")
    print(json.dumps(sequential_elements[:10], indent=4, ensure_ascii=False))  # Afficher les 10 premiers éléments

    # Sauvegarder tous les éléments séquentiels dans un fichier JSON
    sequential_output_file = "sequential_elements.json"
    try:
        with open(sequential_output_file, "w", encoding="utf-8") as f:
            json.dump(sequential_elements, f, indent=4, ensure_ascii=False)
        logger.info("Éléments séquentiels exportés vers %s", sequential_output_file)
    except Exception as e:
        logger.error("Erreur lors de l'écriture du fichier JSON : %s", e)


if __name__ == "__main__":
    main()