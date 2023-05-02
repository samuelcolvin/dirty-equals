import logging
import os
import re

from mkdocs.config import Config
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

try:
    import pytest
except ImportError:
    pytest = None

logger = logging.getLogger('mkdocs.test_examples')


def on_pre_build(config: Config):
    pass


def on_files(files: Files, config: Config) -> Files:
    return remove_files(files)


def remove_files(files: Files) -> Files:
    to_remove = []
    for file in files:
        if file.src_path in {'plugins.py'}:
            to_remove.append(file)
        elif file.src_path.startswith('__pycache__/'):
            to_remove.append(file)

    logger.debug('removing files: %s', [f.src_path for f in to_remove])
    for f in to_remove:
        files.remove(f)

    return files


def on_page_markdown(markdown: str, page: Page, config: Config, files: Files) -> str:
    return add_version(markdown, page)


def add_version(markdown: str, page: Page) -> str:
    if page.file.src_uri == 'index.md':
        version_ref = os.getenv('GITHUB_REF')
        if version_ref and version_ref.startswith('refs/tags/'):
            version = re.sub('^refs/tags/', '', version_ref.lower())
            url = f'https://github.com/samuelcolvin/dirty-equals/releases/tag/{version}'
            version_str = f'Documentation for version: [{version}]({url})'
        elif sha := os.getenv('GITHUB_SHA'):
            sha = sha[:7]
            url = f'https://github.com/samuelcolvin/dirty-equals/commit/{sha}'
            version_str = f'Documentation for development version: [{sha}]({url})'
        else:
            version_str = 'Documentation for development version'
        markdown = re.sub(r'{{ *version *}}', version_str, markdown)
    return markdown
