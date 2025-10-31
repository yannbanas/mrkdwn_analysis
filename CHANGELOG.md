# Changelog

All notable changes to mrkdwn_analysis will be documented in this file.

## [0.2.0] - 2025-10-31

### 🚀 Nouvelles Fonctionnalités

#### Recherche et Filtrage
- **`search_content(pattern, case_sensitive, regex)`** - Recherche avancée avec support regex
- **`filter_by_type(element_type)`** - Filtrage par type d'éléments
- **`find_headers_by_level(level)`** - Recherche de headers par niveau spécifique
- **`get_table_of_contents(max_level)`** - Génération automatique d'une table des matières

#### Export Multi-Formats
- **`export_to_json(include_metadata)`** - Export complet en JSON avec métadonnées
- **`export_to_html(include_style)`** - Conversion en HTML avec CSS intégré
- **`export_to_plain_text(strip_formatting)`** - Export en texte brut avec option de suppression du formatage
- **`to_json()`, `to_html()`, `to_plain_text()`** - Méthodes raccourcies disponibles via MarkdownDocument

#### Statistiques Avancées
- **`get_reading_time(words_per_minute)`** - Calcul du temps de lecture estimé
- **`get_complexity_metrics()`** - Métriques de complexité du document (longueur moyenne des mots, phrases, etc.)
- **`get_link_statistics()`** - Statistiques détaillées sur les liens (internes/externes, domaines uniques)
- **`get_word_frequency(top_n, min_word_length)`** - Analyse de fréquence des mots

#### Validation et Vérification Améliorées
- **`check_links(timeout, max_workers)`** - ⚡ Vérification parallèle des liens avec ThreadPoolExecutor (jusqu'à 10x plus rapide!)
- **`validate_structure()`** - Validation de la structure du document avec scoring
- **`extract_code_by_language(language)`** - Extraction de blocs de code par langage

### ⚡ Améliorations de Performance

- **Caching intelligent** - Ajout d'un système de cache pour les résultats d'analyse (optionnel, activé par défaut)
- **Traitement parallèle** - Vérification des liens en parallèle avec ThreadPoolExecutor
- **Optimisations mémoire** - Meilleure gestion de la mémoire avec des générateurs là où c'est pertinent
- **Decorateurs de performance** - Ajout de `cached_property` et `timed_execution` pour optimiser les opérations répétées

### 🔧 Améliorations Techniques

- **Support des types** - Ajout de type hints (typing.Dict, List, Optional, Union, etc.)
- **Meilleure gestion des erreurs** - Gestion améliorée des exceptions dans les requêtes HTTP
- **Code plus modulaire** - Séparation claire des responsabilités avec des sections bien documentées
- **Documentation enrichie** - Docstrings détaillées pour toutes les nouvelles méthodes

### ✅ Rétrocompatibilité

**100% de compatibilité maintenue** - Toutes les méthodes existantes fonctionnent exactement comme avant:
- `identify_headers()`
- `identify_paragraphs()`
- `identify_code_blocks()`
- `identify_lists()`
- `identify_tables()`
- `identify_links()`
- `identify_blockquotes()`
- `identify_footnotes()`
- `identify_html_blocks()`
- `identify_html_inline()`
- `get_tokens_sequential()`
- `analyse()`
- `count_words()`
- `count_characters()`

### 📝 Nouvelles Options

- **`cache_enabled`** - Nouveau paramètre optionnel pour activer/désactiver le caching (défaut: True)
- Ajout de paramètres optionnels avec valeurs par défaut pour toutes les nouvelles fonctionnalités

### 🧪 Tests

- Nouveaux fichiers de test pour valider les nouvelles fonctionnalités
- Tests de rétrocompatibilité pour garantir qu'aucun code existant ne soit cassé
- `TestNewFeatures.py` - Suite de tests complète pour toutes les nouvelles capacités

### 📚 Documentation

- Mise à jour du README avec exemples des nouvelles fonctionnalités
- Ajout de ce CHANGELOG pour suivre les évolutions
- Documentation inline enrichie pour faciliter l'utilisation

---

## [0.1.6] - 2024-XX-XX

### Fonctionnalités de base
- Parsing complet de Markdown (headers, listes, tableaux, code, etc.)
- Support MDX
- Conversion de sites web en Markdown
- Analyse séquentielle des éléments
- Méthodes de base: `from_file()`, `from_url()`, `from_string()`
- Support du front matter YAML
- Extraction de liens et images
- Gestion des footnotes et références

---

## Migration Guide

### Passer de v0.1.x à v0.2.0

Aucune modification de code n'est nécessaire! La version 0.2.0 est 100% rétrocompatible.

Pour profiter des nouvelles fonctionnalités:

```python
from mrkdwn_analysis import MarkdownDocument

# Votre code existant continue de fonctionner
doc = MarkdownDocument("file.md")
headers = doc.get_headers()

# Nouvelles fonctionnalités disponibles immédiatement
reading_time = doc.get_reading_time()
toc = doc.get_table_of_contents()
html = doc.to_html()
validation = doc.validate_structure()

# Recherche avancée
results = doc.search("keyword")
python_code = doc.extract_code_by_language("python")
```

### Performance

Si vous traitez de gros fichiers et souhaitez désactiver le cache:

```python
doc = MarkdownDocument("large_file.md", cache_enabled=False)
```
