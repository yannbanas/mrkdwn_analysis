from setuptools import setup, find_packages

# Lire le contenu du fichier README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='markdown_analysis',
    version='0.1.5',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='yannbanas',
    author_email='yannbanas@gmail.com',
    url='https://github.com/yannbanas/mrkdwn_analysis',
    packages=find_packages(),
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