import logging
import os
import re

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


def add_version(markdown: str, page: Page, config, files) -> str:
    if page.abs_url == '/':
        version_ref = os.getenv('GITHUB_REF')
        if version_ref:
            version = re.sub('^refs/tags/', '', version_ref.lower())
            version_str = f'Documentation for version: **{version}**'
        else:
            version_str = 'Documentation for development version'
        markdown = re.sub(r'{{ *version *}}', version_str, markdown)
    return markdown
