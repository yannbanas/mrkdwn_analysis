import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import corrigé depuis votre package local
from mrkdwn_analysis import MarkdownDocument

def analyze_markdown_string(markdown_string):
    """
    Analyse une chaîne de texte Markdown et affiche les éléments séquentiels.
    
    Args:
        markdown_string (str): Le contenu Markdown à analyser
    """
    try:
        # Écrire la chaîne dans un fichier temporaire
        temp_file = "temp_markdown.md"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(markdown_string)
        
        # Création de l'objet MarkdownDocument qui encapsule l'analyse du document
        doc = MarkdownDocument(temp_file, from_url=False)
        
        # Obtenir et afficher les éléments séquentiels
        sequential_elements = doc.get_sequential_elements()
        print("\n=== Éléments séquentiels ===")
        print(json.dumps(sequential_elements[:10], indent=4, ensure_ascii=False))  # Afficher les 10 premiers éléments
        
        # Récupération du résumé de l'analyse pour info complémentaire
        summary = doc.get_summary()
        print("\n=== Résumé de l'analyse ===")
        print(json.dumps(summary, indent=4, ensure_ascii=False))
        
        return sequential_elements
        
    except Exception as e:
        logger.error("Erreur lors de l'analyse du markdown : %s", e)
        return None
    
# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple de contenu Markdown
    markdown_example = """# Titre principal
    
## Section 1
Voici un paragraphe avec un **texte en gras** et *italique*.
- Item 1 de la liste
- Item 2 de la liste
  - Sous-item A
  - Sous-item B

## Section 2
Voici un [lien vers Google](https://www.google.com).

### Sous-section 2.1
```python
def hello_world():
    print("Hello, World!")
```

## Section 3
> Ceci est une citation
> Sur plusieurs lignes

![Une image](https://example.com/image.jpg)

1. Premier élément numéroté
2. Deuxième élément numéroté
"""
    
    # Analyser le Markdown
    result = analyze_markdown_string(markdown_example)
    
    # Exemple d'utilisation des résultats
    if result:
        print(f"\nNombre total d'éléments séquentiels : {len(result)}")
        
        # Afficher les types d'éléments trouvés
        element_types = set(elem["type"] for elem in result)
        print(f"Types d'éléments trouvés : {', '.join(element_types)}")