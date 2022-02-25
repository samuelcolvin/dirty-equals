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


def test_examples(config):
    """
    Plug called by mkdocs-simple-hooks to run the examples tests.
    """
    if not pytest:
        logger.info('pytest not installed, skipping examples tests')
    else:
        logger.info('running examples tests...')
        return_code = pytest.main(['-q', '-p', 'no:sugar', 'tests/test_docs.py'])
        if return_code != 0:
            logger.warning('examples tests failed')


def on_page_markdown(markdown: str, page: Page, config: Config, files: Files) -> str:
    markdown = reinstate_code_title(markdown)
    return add_version(markdown, page)


def add_version(markdown: str, page: Page) -> str:
    if page.abs_url == '/':
        version_ref = os.getenv('GITHUB_REF')
        if version_ref:
            version = re.sub('^refs/tags/', '', version_ref.lower())
            version_str = f'Documentation for version: **{version}**'
        else:
            version_str = 'Documentation for development version'
        markdown = re.sub(r'{{ *version *}}', version_str, markdown)
    return markdown


def reinstate_code_title(markdown: str) -> str:
    """
    Fix titles in code blocks, see https://youtrack.jetbrains.com/issue/PY-53246.
    """
    return re.sub(r'^(```py)\s*\ntitle=', r'\1 title=', markdown, flags=re.M)
