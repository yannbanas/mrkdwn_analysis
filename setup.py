from setuptools import setup, find_packages

# Lire le contenu du fichier README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mrkdwn_analysis',  # Changé pour correspondre au nom du dossier
    version='0.1.6',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='yannbanas',
    author_email='yannbanas@gmail.com',
    url='https://github.com/yannbanas/mrkdwn_analysis',
    packages=['mrkdwn_analysis'],  # Spécifiez explicitement le package au lieu de find_packages()
    install_requires=[
        'urllib3',
        'requests',
        'beautifulsoup4',
        'markdownify'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
)