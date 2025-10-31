#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test fonctionnel de check_links() avec des liens dans des paragraphes
(Les liens dans les listes ne sont pas parsés par le parser inline actuel)
"""

from mrkdwn_analysis import MarkdownDocument

# Document de test - les liens doivent être dans des paragraphes, headers ou blockquotes
markdown = """# Test de check_links()

## Liens dans des paragraphes

Voici quelques liens valides: [Google](https://www.google.com) et [GitHub](https://github.com).

Encore un lien vers [Python](https://www.python.org) et un vers [Wikipedia](https://wikipedia.org).

> Une citation avec un [lien dans une blockquote](https://docs.python.org).

### Lien dans un header [Stack Overflow](https://stackoverflow.com)

Liens locaux qui ne seront pas vérifiés: [Fichier](./file.md) et [Ancre](#section).
"""

print("Test de check_links() - Version fonctionnelle")
print("=" * 60)

# Créer le document
doc = MarkdownDocument(markdown, from_string=True)

# Statistiques
print(f"\n📊 Statistiques du document:")
stats = doc.get_link_statistics()
print(f"   Total liens: {stats['total_links']}")
print(f"   Liens externes: {stats['external_links']}")
print(f"   Liens internes: {stats['internal_links']}")

# Obtenir tous les liens
all_links = doc.get_links()
text_links = all_links.get("Text link", [])

print(f"\n🔗 Détail des liens trouvés:")
for link in text_links:
    link_type = "🌐 HTTP" if link['url'].startswith(('http://', 'https://')) else "📄 Local"
    print(f"   {link_type} | Ligne {link['line']:2d} | {link['text']:20s} → {link['url']}")

# Vérifier les liens HTTP
print(f"\n🔍 Vérification des {stats['external_links']} liens HTTP/HTTPS...")
print("   (cela peut prendre quelques secondes...)")

broken_links = doc.check_links(timeout=5, max_workers=10)

# Afficher les résultats
print(f"\n📊 Résultats de la vérification:")

if not broken_links:
    print("   ✅ SUCCÈS: Tous les liens HTTP sont valides!")
    valid_count = stats['external_links']
    print(f"   ✓ {valid_count} lien(s) vérifié(s) avec succès")
else:
    print(f"   ❌ ATTENTION: {len(broken_links)} lien(s) cassé(s) détecté(s):")
    for link in broken_links:
        print(f"\n      🔴 {link['text']}")
        print(f"         URL: {link['url']}")
        print(f"         Ligne: {link['line']}")
        if 'status_code' in link:
            print(f"         Code HTTP: {link['status_code']}")
        if 'error' in link:
            print(f"         Erreur: {link['error']}")

    # Calculer le taux de succès
    valid_count = stats['external_links'] - len(broken_links)
    success_rate = (valid_count / stats['external_links']) * 100 if stats['external_links'] > 0 else 0
    print(f"\n   📈 Taux de succès: {success_rate:.1f}% ({valid_count}/{stats['external_links']})")

print("\n" + "=" * 60)
print("✅ Test terminé!")
print("\n💡 Note: La méthode check_links() fonctionne sur tous les liens")
print("   HTTP/HTTPS trouvés dans les paragraphes, headers et blockquotes.")
