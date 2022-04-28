import importlib.util
import platform
import re
from pathlib import Path
from textwrap import dedent

import pytest
from _pytest.assertion.rewrite import AssertionRewritingHook

ROOT_DIR = Path(__file__).parent.parent


@pytest.fixture
def import_execute(request, tmp_path: Path):
    def _import_execute(module_name: str, source: str, rewrite_assertions: bool = False):
        if rewrite_assertions:
            loader = AssertionRewritingHook(config=request.config)
            loader.mark_rewrite(module_name)
        else:
            loader = None

        module_path = tmp_path / f'{module_name}.py'
        module_path.write_text(source)
        spec = importlib.util.spec_from_file_location(module_name, str(module_path), loader=loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    return _import_execute


def extract_code_chunks(path: Path, text: str, offset: int):
    rel_path = path.relative_to(ROOT_DIR)
    fences = len(re.findall(r'^```', text, flags=re.M))
    if fences % 2 != 0:
        raise ValueError(
            f'{rel_path}:{offset} has an odd number of code fences (```), might be missing a closing fence'
        )

    for m_code in re.finditer(r'^```(.*?)$\n(.*?)^```', text, flags=re.M | re.S):
        prefix = m_code.group(1).lower()
        if not prefix.startswith(('py', '{.py')) or 'test="false"' in prefix:
            continue

        start_line = offset + text[: m_code.start()].count('\n') + 1
        code = m_code.group(2)
        end_line = start_line + code.count('\n') + 1
        source = '\n' * start_line + code
        yield pytest.param(f'{path.stem}_{start_line}_{end_line}', source, id=f'{rel_path}:{start_line}-{end_line}')


def generate_code_chunks(*directories: str):
    for d in directories:
        for path in (ROOT_DIR / d).glob('**/*'):
            if path.suffix == '.py':
                code = path.read_text()
                for m_docstring in re.finditer(r'(^\s*)r?"""$(.*?)\1"""', code, flags=re.M | re.S):
                    start_line = code[: m_docstring.start()].count('\n')
                    docstring = dedent(m_docstring.group(2))
                    yield from extract_code_chunks(path, docstring, start_line)
            elif path.suffix == '.md':
                code = path.read_text()
                yield from extract_code_chunks(path, code, 0)


def pytest_generate_tests(metafunc):
    metafunc.parametrize('module_name,source_code', generate_code_chunks('dirty_equals', 'docs'))


@pytest.mark.skipif(platform.python_implementation() == 'PyPy', reason='PyPy does not metaclass dunder methods')
def test_docs_examples(module_name, source_code, import_execute):
    import_execute(module_name, source_code, True)
