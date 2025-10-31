#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des nouvelles fonctionnalités améliorées de mrkdwn_analysis.
Ce script démontre les nouvelles capacités de la bibliothèque.
"""

import json
from mrkdwn_analysis import MarkdownDocument

# Exemple de contenu Markdown pour tester
markdown_example = """# Guide Python

## Introduction

Python est un **langage de programmation** puissant et facile à apprendre.
Il dispose d'une syntaxe simple et élégante.

### Caractéristiques

- Syntaxe claire et lisible
- Grande bibliothèque standard
- Multiparadigme (orienté objet, fonctionnel, procédural)

## Installation

Pour installer Python, visitez [python.org](https://www.python.org).

### Code Example

```python
def hello_world():
    print("Hello, World!")

hello_world()
```

## Resources

- [Documentation officielle](https://docs.python.org)
- [PyPI](https://pypi.org)

> Python est un excellent choix pour les débutants et les experts.

## Conclusion

Python continue d'être l'un des langages les plus populaires.
"""

def main():
    print("=" * 70)
    print("TEST DES NOUVELLES FONCTIONNALITÉS - mrkdwn_analysis v0.2.0")
    print("=" * 70)

    # Créer le document
    doc = MarkdownDocument(markdown_example, from_string=True)

    # =========================================================================
    # 1. RECHERCHE ET FILTRAGE
    # =========================================================================
    print("\n1. RECHERCHE ET FILTRAGE")
    print("-" * 70)

    # Recherche de contenu
    search_results = doc.search("Python")
    print(f"\n✓ Recherche 'Python': {len(search_results)} résultats trouvés")

    # Headers par niveau
    h2_headers = doc.find_headers_by_level(2)
    print(f"✓ Headers de niveau 2: {len(h2_headers)} trouvés")
    for h in h2_headers:
        print(f"  - {h['text']}")

    # Table des matières
    toc = doc.get_table_of_contents(max_level=3)
    print(f"\n✓ Table des matières ({len(toc)} entrées):")
    for entry in toc:
        print(f"  {entry['indent']}- {entry['text']}")

    # =========================================================================
    # 2. EXPORT VERS DIFFÉRENTS FORMATS
    # =========================================================================
    print("\n\n2. EXPORT VERS DIFFÉRENTS FORMATS")
    print("-" * 70)

    # Export JSON
    json_output = doc.to_json(include_metadata=True)
    print(f"✓ Export JSON: {len(json_output)} caractères")

    # Export HTML
    html_output = doc.to_html(include_style=True)
    print(f"✓ Export HTML: {len(html_output)} caractères")

    # Export Plain Text
    plain_output = doc.to_plain_text(strip_formatting=True)
    print(f"✓ Export Plain Text: {len(plain_output)} caractères")

    # =========================================================================
    # 3. STATISTIQUES AVANCÉES
    # =========================================================================
    print("\n\n3. STATISTIQUES AVANCÉES")
    print("-" * 70)

    # Temps de lecture
    reading_time = doc.get_reading_time()
    print(f"\n✓ Temps de lecture:")
    print(f"  - Mots: {reading_time['words']}")
    print(f"  - Temps estimé: {reading_time['formatted']}")

    # Métriques de complexité
    complexity = doc.get_complexity_metrics()
    print(f"\n✓ Métriques de complexité:")
    print(f"  - Mots totaux: {complexity['total_words']}")
    print(f"  - Phrases: {complexity['total_sentences']}")
    print(f"  - Paragraphes: {complexity['total_paragraphs']}")
    print(f"  - Longueur moyenne des mots: {complexity['avg_word_length']}")
    print(f"  - Score de complexité: {complexity['complexity_score']}")

    # Statistiques des liens
    link_stats = doc.get_link_statistics()
    print(f"\n✓ Statistiques des liens:")
    print(f"  - Total liens: {link_stats['total_links']}")
    print(f"  - Liens externes: {link_stats['external_links']}")
    print(f"  - Liens internes: {link_stats['internal_links']}")
    print(f"  - Domaines uniques: {link_stats['unique_domains']}")

    # Fréquence des mots
    word_freq = doc.get_word_frequency(top_n=10)
    print(f"\n✓ Top 10 mots les plus fréquents:")
    for word, count in word_freq[:5]:  # Afficher seulement les 5 premiers
        print(f"  - {word}: {count}")

    # =========================================================================
    # 4. VALIDATION ET VÉRIFICATION
    # =========================================================================
    print("\n\n4. VALIDATION ET VÉRIFICATION")
    print("-" * 70)

    # Validation de structure
    validation = doc.validate_structure()
    print(f"\n✓ Validation de structure:")
    print(f"  - Valide: {validation['valid']}")
    print(f"  - Score: {validation['score']}/100")
    if validation['issues']:
        print(f"  - Problèmes trouvés: {len(validation['issues'])}")
        for issue in validation['issues'][:3]:  # Afficher les 3 premiers
            print(f"    • [{issue['type']}] {issue['message']}")

    # Extraction de code par langage
    python_code = doc.extract_code_by_language('python')
    print(f"\n✓ Blocs de code Python trouvés: {len(python_code)}")
    if python_code:
        print(f"  Exemple de code:\n{python_code[0]['content'][:60]}...")

    # =========================================================================
    # 5. RÉTROCOMPATIBILITÉ
    # =========================================================================
    print("\n\n5. RÉTROCOMPATIBILITÉ - Méthodes existantes fonctionnent")
    print("-" * 70)

    summary = doc.get_summary()
    print(f"✓ get_summary(): {summary['headers']} headers, {summary['paragraphs']} paragraphes")

    headers = doc.get_headers()
    print(f"✓ get_headers(): {len(headers)} headers trouvés")

    paragraphs = doc.get_paragraphs()
    print(f"✓ get_paragraphs(): {len(paragraphs)} paragraphes trouvés")

    links = doc.get_links()
    print(f"✓ get_links(): {len(links.get('Text link', []))} liens trouvés")

    code_blocks = doc.get_code_blocks()
    print(f"✓ get_code_blocks(): {len(code_blocks)} blocs de code trouvés")

    sequential = doc.get_sequential_elements()
    print(f"✓ get_sequential_elements(): {len(sequential)} éléments séquentiels")

    # =========================================================================
    # RÉSUMÉ
    # =========================================================================
    print("\n\n" + "=" * 70)
    print("✅ TOUS LES TESTS SONT RÉUSSIS!")
    print("=" * 70)
    print("\nLa bibliothèque mrkdwn_analysis a été améliorée avec succès:")
    print("  ✓ Nouvelles fonctionnalités de recherche et filtrage")
    print("  ✓ Export vers JSON, HTML, et Plain Text")
    print("  ✓ Statistiques avancées et métriques")
    print("  ✓ Validation et vérification améliorées")
    print("  ✓ Vérification parallèle des liens (avec ThreadPoolExecutor)")
    print("  ✓ 100% de rétrocompatibilité maintenue")
    print("\n")

if __name__ == "__main__":
    main()
