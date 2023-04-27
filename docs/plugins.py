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
    test_examples()


def test_examples():
    """
    Run the examples tests.
    """
    try:
        run_pytest = getattr('pytest', 'main')
    except AttributeError:
        logger.info('pytest not installed, skipping examples tests')
    else:
        logger.info('running examples tests...')
        return_code = run_pytest(['-q', '-p', 'no:sugar', 'tests/test_docs.py'])
        if return_code != 0:
            logger.warning('examples tests failed')


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
    if page.abs_url == '/latest/':
        version_ref = os.getenv('GITHUB_REF')
        if version_ref:
            version = re.sub('^refs/tags/', '', version_ref.lower())
            version_str = f'Documentation for version: **{version}**'
        else:
            version_str = 'Documentation for development version'
        markdown = re.sub(r'{{ *version *}}', version_str, markdown)
    return markdown
