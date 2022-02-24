import logging

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
