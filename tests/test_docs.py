import importlib.util
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
    for m_code in re.finditer(r'^```([^\n]+)\n(.*?)^```', text, flags=re.M | re.S):
        prefix = m_code.group(1).lower()
        if not prefix.startswith(('py', '{.py')) or 'test="false"' in prefix:
            continue

        line_no = offset + text[: m_code.start()].count('\n') + 2
        source = '\n' * line_no + m_code.group(2)
        yield pytest.param(f'{path.stem}_{line_no}', source, id=f'{path.name}:{line_no}')


def generate_code_chunks(directory: Path):
    for path in directory.glob('**/*'):
        if path.suffix == '.py':
            code = path.read_text()
            for m_docstring in re.finditer(r'^(\s*"""\n)(.*?)\n\1', code, flags=re.M | re.S):
                start_line = code[: m_docstring.start()].count('\n') + 1
                docstring = dedent(m_docstring.group(2))
                yield from extract_code_chunks(path, docstring, start_line)
        elif path.suffix == '.md':
            code = path.read_text()
            yield from extract_code_chunks(path, code, 0)


@pytest.mark.parametrize('module_name,source_code', generate_code_chunks(ROOT_DIR / 'dirty_equals'))
def test_docstring_examples(module_name, source_code, import_execute):
    import_execute(module_name, source_code)


@pytest.mark.parametrize('module_name,source_code', generate_code_chunks(ROOT_DIR / 'docs'))
def test_docs_examples(module_name, source_code, import_execute):
    import_execute(module_name, source_code)
