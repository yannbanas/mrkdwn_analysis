#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple et rapide de check_links()
"""

from mrkdwn_analysis import MarkdownDocument

# Document de test avec liens variés
markdown = """
# Test de check_links()

## Liens valides
- [Google](https://www.google.com)
- [GitHub](https://github.com)

## Liens locaux (non vérifiés)
- [Fichier local](./file.md)
- [Ancre](#section)
"""

print("Test de la méthode check_links()")
print("=" * 50)

# Créer le document
doc = MarkdownDocument(markdown, from_string=True)

# Obtenir les liens
all_links = doc.get_links()
text_links = all_links.get("Text link", [])

print(f"\n📋 Liens trouvés dans le document: {len(text_links)}")
for link in text_links:
    link_type = "HTTP" if link['url'].startswith(('http://', 'https://')) else "Local"
    print(f"   [{link_type}] {link['text']} → {link['url']}")

# Vérifier les liens
print(f"\n🔍 Vérification des liens HTTP...")
broken_links = doc.check_links(timeout=5, max_workers=5)

# Afficher le résultat
print(f"\n📊 Résultat:")
if not broken_links:
    print("   ✅ Tous les liens HTTP sont valides!")
else:
    print(f"   ❌ {len(broken_links)} lien(s) cassé(s):")
    for link in broken_links:
        print(f"      - {link['url']}")
        if 'status_code' in link:
            print(f"        Code: {link['status_code']}")
        if 'error' in link:
            print(f"        Erreur: {link['error']}")

print("\n✅ Test terminé!")
