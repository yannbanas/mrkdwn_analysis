# Documentation: check_links()

## 📋 Vue d'ensemble

La méthode `check_links()` permet de **vérifier automatiquement tous les liens HTTP/HTTPS** présents dans un document Markdown. Elle utilise le traitement parallèle (ThreadPoolExecutor) pour une performance optimale.

## ✅ Oui, la méthode est implémentée!

La méthode `check_links()` est **pleinement implémentée et fonctionnelle** dans la version 0.2.0 de mrkdwn_analysis. Elle est disponible via:
- La classe `MarkdownAnalyzer` (bas niveau)
- La classe `MarkdownDocument` (recommandé, haut niveau)

## 🚀 Utilisation de base

### Import et création du document

```python
from mrkdwn_analysis import MarkdownDocument

# Depuis un fichier
doc = MarkdownDocument("document.md")

# Depuis une URL
doc = MarkdownDocument.from_url("https://example.com/doc.md")

# Depuis une chaîne de caractères
markdown_text = """
# Mon Document
[Lien valide](https://www.google.com)
[Lien cassé](https://httpstat.us/404)
"""
doc = MarkdownDocument(markdown_text, from_string=True)
```

### Vérification des liens

```python
# Utilisation avec paramètres par défaut
broken_links = doc.check_links()

# Avec paramètres personnalisés
broken_links = doc.check_links(
    timeout=5,        # Timeout de 5 secondes par lien
    max_workers=10    # 10 vérifications en parallèle
)
```

## 📊 Format de retour

La méthode retourne une **liste de dictionnaires**, un pour chaque lien cassé ou en erreur:

```python
[
    {
        'url': 'https://example.com/broken',
        'line': 42,                          # Numéro de ligne dans le document
        'text': 'Texte du lien',
        'status_code': 404                   # Code HTTP (si disponible)
    },
    {
        'url': 'https://timeout.com',
        'line': 58,
        'text': 'Lien timeout',
        'error': 'Connection timeout'       # Message d'erreur (si exception)
    }
]
```

Si tous les liens sont valides, la méthode retourne une **liste vide** `[]`.

## ⚙️ Paramètres

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `timeout` | int | 5 | Temps d'attente maximum en secondes pour chaque requête |
| `max_workers` | int | 10 | Nombre de vérifications parallèles (ThreadPoolExecutor) |
| `follow_redirects` | bool | True | Suivre les redirections HTTP (disponible sur MarkdownAnalyzer) |

### Notes sur les paramètres

- **timeout**: Augmentez pour des sites lents, diminuez pour plus de rapidité
- **max_workers**: Plus de workers = plus rapide, mais plus de charge réseau
- **follow_redirects**: La plupart des sites utilisent des redirections (http → https), mieux vaut laisser à True

## 💡 Exemples pratiques

### Exemple 1: Vérification simple

```python
from mrkdwn_analysis import MarkdownDocument

doc = MarkdownDocument("README.md")
broken_links = doc.check_links()

if not broken_links:
    print("✅ Tous les liens sont valides!")
else:
    print(f"❌ {len(broken_links)} lien(s) cassé(s):")
    for link in broken_links:
        print(f"  - {link['url']} (ligne {link['line']})")
```

### Exemple 2: Rapport détaillé

```python
from mrkdwn_analysis import MarkdownDocument

doc = MarkdownDocument("documentation.md")

# Obtenir d'abord les statistiques
link_stats = doc.get_link_statistics()
print(f"Total de liens: {link_stats['total_links']}")
print(f"Liens externes: {link_stats['external_links']}")

# Vérifier les liens
broken_links = doc.check_links(timeout=10, max_workers=15)

# Analyser les résultats
for link in broken_links:
    print(f"\n⚠️  Lien cassé détecté:")
    print(f"   Texte: {link['text']}")
    print(f"   URL: {link['url']}")
    print(f"   Ligne: {link['line']}")

    if 'status_code' in link:
        if link['status_code'] == 404:
            print(f"   ❌ Page non trouvée (404)")
        elif link['status_code'] >= 500:
            print(f"   🔴 Erreur serveur ({link['status_code']})")
        else:
            print(f"   Code: {link['status_code']}")

    if 'error' in link:
        print(f"   ⚠️  Erreur: {link['error']}")
```

### Exemple 3: Workflow automatisé

```python
from mrkdwn_analysis import MarkdownDocument
import json

def validate_markdown_file(filepath):
    """Valide un fichier Markdown et retourne un rapport."""
    doc = MarkdownDocument(filepath)

    # Validation de structure
    structure = doc.validate_structure()

    # Vérification des liens
    broken_links = doc.check_links(timeout=5, max_workers=10)

    # Statistiques
    stats = doc.get_link_statistics()

    # Créer le rapport
    report = {
        'file': filepath,
        'structure_score': structure['score'],
        'structure_valid': structure['valid'],
        'total_links': stats['total_links'],
        'external_links': stats['external_links'],
        'broken_links_count': len(broken_links),
        'broken_links': broken_links,
        'success_rate': 0
    }

    if stats['external_links'] > 0:
        valid = stats['external_links'] - len(broken_links)
        report['success_rate'] = (valid / stats['external_links']) * 100

    return report

# Utilisation
report = validate_markdown_file("documentation.md")
print(json.dumps(report, indent=2, ensure_ascii=False))

if report['broken_links_count'] == 0:
    print("\n✅ Document valide, tous les liens fonctionnent!")
else:
    print(f"\n⚠️  Attention: {report['broken_links_count']} lien(s) cassé(s)")
```

### Exemple 4: Traiter plusieurs fichiers

```python
from mrkdwn_analysis import MarkdownDocument
import glob

def check_all_markdown_files(directory="docs"):
    """Vérifie tous les fichiers Markdown d'un répertoire."""
    results = {}

    for filepath in glob.glob(f"{directory}/**/*.md", recursive=True):
        print(f"🔍 Vérification: {filepath}")

        try:
            doc = MarkdownDocument(filepath)
            broken_links = doc.check_links(timeout=5, max_workers=10)

            results[filepath] = {
                'status': 'ok' if not broken_links else 'error',
                'broken_count': len(broken_links),
                'broken_links': broken_links
            }

        except Exception as e:
            results[filepath] = {
                'status': 'failed',
                'error': str(e)
            }

    return results

# Utilisation
results = check_all_markdown_files("docs")

# Afficher le résumé
total_files = len(results)
files_with_errors = sum(1 for r in results.values() if r['status'] == 'error')
total_broken = sum(r.get('broken_count', 0) for r in results.values())

print(f"\n📊 Résumé:")
print(f"   Fichiers analysés: {total_files}")
print(f"   Fichiers avec liens cassés: {files_with_errors}")
print(f"   Total liens cassés: {total_broken}")
```

## 🔍 Comportement de la méthode

### Liens vérifiés
✅ **Vérifiés:**
- `https://example.com`
- `http://example.com`
- Tous les liens HTTP/HTTPS

❌ **Non vérifiés (ignorés):**
- `#section` (ancres internes)
- `./file.md` (chemins relatifs)
- `/absolute/path` (chemins absolus locaux)
- `mailto:email@example.com`
- `ftp://example.com`

### Méthode de vérification

1. **Première tentative**: Requête `HEAD` (rapide, ne télécharge pas le contenu)
2. **Si échec 405**: Requête `GET` avec streaming (certains serveurs n'acceptent pas HEAD)
3. **Vérification du code de statut**:
   - Code 200-399 → Lien valide ✅
   - Code 400+ → Lien cassé ❌

### Performance

Grâce au `ThreadPoolExecutor`:
- **Sans parallélisme**: ~2 secondes par lien
- **Avec parallélisme (10 workers)**: ~0.2 secondes par lien en moyenne
- **Gain de performance**: **~10x plus rapide** pour documents avec nombreux liens

**Exemple**: Vérifier 50 liens
- Sans parallélisme: ~100 secondes
- Avec parallélisme: ~10 secondes

## ⚠️ Gestion des erreurs

### Codes HTTP courants

| Code | Signification | Action recommandée |
|------|--------------|-------------------|
| 200 | OK | Lien valide |
| 301/302 | Redirection | Généralement OK (suivie automatiquement) |
| 404 | Not Found | Mettre à jour ou supprimer le lien |
| 403 | Forbidden | Vérifier les permissions ou le lien |
| 500-599 | Erreur serveur | Réessayer plus tard |
| Timeout | Pas de réponse | Augmenter le timeout ou vérifier le lien |

### Exceptions gérées

```python
try:
    broken_links = doc.check_links()
except Exception as e:
    print(f"Erreur lors de la vérification: {e}")
```

Les exceptions sont gérées en interne et retournées dans le champ `'error'` du résultat.

## 🎯 Cas d'usage

### 1. CI/CD - Vérification automatique

```bash
# Script Python pour CI/CD
python check_docs.py
exit $?  # Retourne code d'erreur si liens cassés
```

```python
# check_docs.py
import sys
from mrkdwn_analysis import MarkdownDocument

doc = MarkdownDocument("README.md")
broken = doc.check_links()

if broken:
    print(f"❌ CI Failed: {len(broken)} broken links")
    sys.exit(1)
else:
    print("✅ CI Passed: All links valid")
    sys.exit(0)
```

### 2. Pre-commit hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
python -c "
from mrkdwn_analysis import MarkdownDocument
import sys
doc = MarkdownDocument('README.md')
broken = doc.check_links()
if broken:
    print('⚠️  Warning: README has broken links')
    for link in broken:
        print(f'  - {link[\"url\"]}')
    sys.exit(1)
"
```

### 3. Rapport périodique

```python
# Créer un rapport hebdomadaire
import schedule
import time

def weekly_check():
    doc = MarkdownDocument("docs/main.md")
    broken = doc.check_links()

    # Envoyer email ou notification
    if broken:
        send_notification(f"{len(broken)} broken links found!")

schedule.every().monday.at("09:00").do(weekly_check)

while True:
    schedule.run_pending()
    time.sleep(3600)
```

## 🔧 Configuration avancée

### Utilisation directe de MarkdownAnalyzer

```python
from mrkdwn_analysis import MarkdownAnalyzer

# Avec plus de contrôle sur follow_redirects
analyzer = MarkdownAnalyzer.from_string(markdown_text)
broken = analyzer.check_links(
    timeout=10,
    max_workers=20,
    follow_redirects=False  # Ne pas suivre les redirections
)
```

### Personnalisation du timeout par domaine

```python
from mrkdwn_analysis import MarkdownDocument

doc = MarkdownDocument("docs.md")

# Vérification rapide d'abord
quick_check = doc.check_links(timeout=2, max_workers=10)

# Re-vérifier les erreurs avec timeout plus long
if quick_check:
    slow_urls = [link['url'] for link in quick_check]
    # Implémenter une re-vérification personnalisée
```

## 📚 Documentation complémentaire

Pour voir toutes les méthodes disponibles:
- `doc.get_links()` - Obtenir tous les liens
- `doc.get_link_statistics()` - Statistiques détaillées
- `doc.validate_structure()` - Valider la structure du document
- `doc.search()` - Rechercher du contenu

## 🐛 Dépannage

### "No module named 'requests'"

```bash
pip install requests beautifulsoup4 markdownify urllib3
```

### Timeouts fréquents

```python
# Augmenter le timeout
broken = doc.check_links(timeout=15)  # 15 secondes
```

### Trop lent

```python
# Augmenter les workers
broken = doc.check_links(max_workers=20)  # Plus rapide
```

### Faux positifs (liens valides détectés comme cassés)

```python
# Certains sites bloquent les requêtes automatiques
# Vérifier manuellement ou ajouter des headers personnalisés
# (nécessite modification du code source)
```

## ✅ Résumé

**check_links()** est une méthode puissante et performante pour:
- ✅ Vérifier automatiquement tous les liens HTTP/HTTPS
- ✅ Traitement parallèle (10x plus rapide)
- ✅ Gestion complète des erreurs
- ✅ Intégration facile dans CI/CD
- ✅ Rapports détaillés avec ligne et contexte

**Utilisation recommandée:**
```python
from mrkdwn_analysis import MarkdownDocument

doc = MarkdownDocument("document.md")
broken_links = doc.check_links(timeout=5, max_workers=10)

if broken_links:
    print(f"⚠️  {len(broken_links)} lien(s) à corriger")
```
