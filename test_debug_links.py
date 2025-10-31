#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug des liens
"""

from mrkdwn_analysis import MarkdownDocument

# Document de test avec liens
markdown = """# Test de check_links()

## Liens valides
- [Google](https://www.google.com)
- [GitHub](https://github.com)
- [Python](https://www.python.org)

## Liens locaux
- [Fichier](./file.md)
- [Ancre](#section)
"""

print("Debug de l'extraction des liens")
print("=" * 50)
print(f"\nContenu Markdown:\n{markdown}")

# Créer le document
doc = MarkdownDocument(markdown, from_string=True)

# Obtenir tous les tokens
print("\n📋 Tokens parsés:")
for i, token in enumerate(doc.analyzer.tokens[:10], 1):
    print(f"   {i}. Type: {token.type}, Content: {token.content[:50] if token.content else 'N/A'}")

# Obtenir les liens
all_links = doc.get_links()
print(f"\n🔗 Liens identifiés:")
print(f"   Text links: {all_links.get('Text link', [])}")
print(f"   Image links: {all_links.get('Image link', [])}")

# Vérifier les liens
print(f"\n🔍 Vérification des liens HTTP...")
broken_links = doc.check_links(timeout=5, max_workers=5)

print(f"\n📊 Résultat:")
print(f"   Liens cassés: {len(broken_links)}")
if not broken_links:
    print("   ✅ Tous valides!")
else:
    for link in broken_links:
        print(f"      - {link}")
