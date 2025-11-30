from mrkdwn_analysis import MarkdownParser

# Cas qui causaient la boucle infinie
test_cases = [
    "===",
    "===\n",
    "\n===\n",
    "---\n",
    "Titre\n===",  # Devrait créer un header
]

for markdown_text in test_cases:
    print(f"Test: {repr(markdown_text)}")
    try:
        parser = MarkdownParser(markdown_text)
        tokens = parser.parse()
        print(f"  ✓ Succès - {len(tokens)} tokens")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")