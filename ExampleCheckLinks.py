#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemple d'utilisation de la méthode check_links()
pour vérifier les liens dans un document Markdown.
"""

from mrkdwn_analysis import MarkdownDocument

# Exemple 1: Document Markdown avec différents types de liens
markdown_content = """# Mon Document de Test

## Section avec liens valides

Voici quelques liens vers des sites populaires:
- [Google](https://www.google.com)
- [GitHub](https://github.com)
- [Python Documentation](https://docs.python.org)

## Section avec liens potentiellement cassés

Attention, ces liens peuvent être cassés:
- [Lien cassé 1](https://httpstat.us/404)
- [Lien cassé 2](https://httpstat.us/500)
- [Lien timeout](https://httpstat.us/200?sleep=10000)

## Liens internes et non-HTTP

Ces liens ne seront pas vérifiés (car non-HTTP):
- [Lien interne](#section)
- [Fichier local](./fichier.md)

## Plus de liens externes

- [Wikipedia](https://wikipedia.org)
- [Stack Overflow](https://stackoverflow.com)
"""

def example_basic():
    """Exemple basique de vérification des liens."""
    print("=" * 70)
    print("EXEMPLE 1: Vérification basique des liens")
    print("=" * 70)

    # Créer le document depuis une chaîne
    doc = MarkdownDocument(markdown_content, from_string=True)

    # Vérifier tous les liens (avec paramètres par défaut)
    print("\n🔍 Vérification des liens en cours...")
    broken_links = doc.check_links()

    # Afficher les résultats
    if not broken_links:
        print("✅ Tous les liens sont valides!")
    else:
        print(f"❌ {len(broken_links)} lien(s) cassé(s) trouvé(s):\n")
        for link in broken_links:
            print(f"  ⚠️  Ligne {link['line']}: {link['text']}")
            print(f"      URL: {link['url']}")
            if 'status_code' in link:
                print(f"      Code HTTP: {link['status_code']}")
            if 'error' in link:
                print(f"      Erreur: {link['error']}")
            print()

def example_with_parameters():
    """Exemple avec paramètres personnalisés."""
    print("\n" + "=" * 70)
    print("EXEMPLE 2: Vérification avec paramètres personnalisés")
    print("=" * 70)

    doc = MarkdownDocument(markdown_content, from_string=True)

    # Paramètres:
    # - timeout: 3 secondes (plus rapide)
    # - max_workers: 5 (moins de connexions parallèles)
    print("\n🔍 Vérification avec timeout=3s, max_workers=5...")
    broken_links = doc.check_links(timeout=3, max_workers=5)

    print(f"Résultat: {len(broken_links)} lien(s) problématique(s)")

def example_from_file():
    """Exemple depuis un fichier Markdown."""
    print("\n" + "=" * 70)
    print("EXEMPLE 3: Vérification depuis le README.md")
    print("=" * 70)

    try:
        # Lire le README.md du projet
        doc = MarkdownDocument("README.md")

        # Obtenir d'abord les statistiques des liens
        link_stats = doc.get_link_statistics()
        print(f"\n📊 Statistiques:")
        print(f"   - Total de liens: {link_stats['total_links']}")
        print(f"   - Liens externes: {link_stats['external_links']}")
        print(f"   - Liens internes: {link_stats['internal_links']}")

        # Vérifier les liens
        print(f"\n🔍 Vérification de {link_stats['external_links']} lien(s) externe(s)...")
        broken_links = doc.check_links(timeout=5, max_workers=10)

        if not broken_links:
            print("✅ Tous les liens externes sont valides!")
        else:
            print(f"❌ {len(broken_links)} lien(s) cassé(s):")
            for link in broken_links:
                print(f"   - {link['url']}")
                if 'status_code' in link:
                    print(f"     Code: {link['status_code']}")

    except FileNotFoundError:
        print("❌ Fichier README.md non trouvé")

def example_comprehensive_report():
    """Exemple avec rapport complet."""
    print("\n" + "=" * 70)
    print("EXEMPLE 4: Rapport complet de validation")
    print("=" * 70)

    doc = MarkdownDocument(markdown_content, from_string=True)

    # 1. Obtenir tous les liens
    all_links = doc.get_links()
    text_links = all_links.get("Text link", [])

    print(f"\n📋 Analyse du document:")
    print(f"   - Total de liens: {len(text_links)}")

    # Séparer les liens HTTP des autres
    http_links = [l for l in text_links if l['url'].startswith(('http://', 'https://'))]
    other_links = [l for l in text_links if not l['url'].startswith(('http://', 'https://'))]

    print(f"   - Liens HTTP/HTTPS: {len(http_links)}")
    print(f"   - Autres liens (internes/locaux): {len(other_links)}")

    # 2. Vérifier les liens HTTP
    if http_links:
        print(f"\n🔍 Vérification des {len(http_links)} liens HTTP...")
        broken_links = doc.check_links(timeout=5, max_workers=10)

        # 3. Calculer les statistiques
        valid_count = len(http_links) - len(broken_links)
        success_rate = (valid_count / len(http_links)) * 100 if http_links else 0

        print(f"\n📊 Résultats de la vérification:")
        print(f"   ✅ Liens valides: {valid_count}")
        print(f"   ❌ Liens cassés: {len(broken_links)}")
        print(f"   📈 Taux de succès: {success_rate:.1f}%")

        # 4. Détails des liens cassés
        if broken_links:
            print(f"\n⚠️  Détails des liens cassés:")
            for i, link in enumerate(broken_links, 1):
                print(f"\n   {i}. Texte: '{link['text']}'")
                print(f"      URL: {link['url']}")
                print(f"      Ligne: {link['line']}")
                if 'status_code' in link:
                    status_emoji = "🔴" if link['status_code'] >= 500 else "🟠"
                    print(f"      {status_emoji} Code HTTP: {link['status_code']}")
                if 'error' in link:
                    print(f"      ⚠️  Erreur: {link['error']}")

def example_validation_workflow():
    """Exemple d'un workflow complet de validation."""
    print("\n" + "=" * 70)
    print("EXEMPLE 5: Workflow complet de validation de document")
    print("=" * 70)

    doc = MarkdownDocument(markdown_content, from_string=True)

    print("\n🔍 ÉTAPE 1: Validation de la structure")
    print("-" * 70)
    structure_validation = doc.validate_structure()
    print(f"Score de structure: {structure_validation['score']}/100")
    if structure_validation['issues']:
        for issue in structure_validation['issues']:
            print(f"  [{issue['type']}] {issue['message']}")
    else:
        print("  ✅ Structure valide")

    print("\n🔍 ÉTAPE 2: Statistiques du document")
    print("-" * 70)
    summary = doc.get_summary()
    print(f"  - Headers: {summary['headers']}")
    print(f"  - Paragraphes: {summary['paragraphs']}")
    print(f"  - Blocs de code: {summary['code_blocks']}")

    reading_time = doc.get_reading_time()
    print(f"  - Temps de lecture: {reading_time['formatted']}")

    print("\n🔍 ÉTAPE 3: Vérification des liens")
    print("-" * 70)
    broken_links = doc.check_links(timeout=5, max_workers=10)
    if not broken_links:
        print("  ✅ Tous les liens sont valides")
    else:
        print(f"  ❌ {len(broken_links)} lien(s) cassé(s)")
        for link in broken_links[:3]:  # Afficher les 3 premiers
            print(f"     - {link['url']}")

    print("\n" + "=" * 70)
    print("✅ VALIDATION TERMINÉE")
    print("=" * 70)

if __name__ == "__main__":
    # Exécuter tous les exemples
    try:
        example_basic()
        example_with_parameters()
        example_from_file()
        example_comprehensive_report()
        example_validation_workflow()

        print("\n\n" + "=" * 70)
        print("📚 RÉSUMÉ DE L'UTILISATION DE check_links()")
        print("=" * 70)
        print("""
La méthode check_links() permet de vérifier tous les liens HTTP/HTTPS
dans un document Markdown de manière parallèle et performante.

SYNTAXE:
--------
broken_links = doc.check_links(timeout=5, max_workers=10)

PARAMÈTRES:
-----------
- timeout (int, défaut=5): Temps d'attente maximum en secondes par lien
- max_workers (int, défaut=10): Nombre de vérifications parallèles

RETOUR:
-------
Liste de dictionnaires pour chaque lien cassé avec:
- 'url': L'URL du lien
- 'line': Numéro de ligne dans le document
- 'text': Texte du lien
- 'status_code': Code HTTP si disponible (404, 500, etc.)
- 'error': Message d'erreur si exception

NOTES:
------
✓ Seuls les liens HTTP/HTTPS sont vérifiés
✓ Les liens internes (#section) et locaux (./file) sont ignorés
✓ Utilise ThreadPoolExecutor pour performance optimale
✓ Tente HEAD puis GET si le serveur ne supporte pas HEAD
        """)

    except KeyboardInterrupt:
        print("\n\n⏹️  Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
