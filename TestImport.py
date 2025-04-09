# test_import.py
try:
    # Option 1: Importer le module lui-même
    import mrkdwn_analysis
    print("Import du module réussi")
    print("Contenu du module:", dir(mrkdwn_analysis))
    
    # Option 2: Vérifier les éléments importés avec "*"
    from mrkdwn_analysis import *
    print("\nÉléments importés avec '*':")
    imported_items = [item for item in dir() if not item.startswith('__') and item != 'mrkdwn_analysis']
    print(imported_items)
    
    # Vérifier spécifiquement si MarkdownDocument est accessible
    print("\nVérification de MarkdownDocument:")
    try:
        print(f"MarkdownDocument existe: {MarkdownDocument is not None}")
    except NameError:
        print("MarkdownDocument n'est pas accessible")
    
except ImportError as e:
    print(f"Erreur d'importation: {e}")