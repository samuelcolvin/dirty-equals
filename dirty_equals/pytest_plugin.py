from __future__ import annotations as _annotations

import ast
import os
import sys
import textwrap
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from itertools import groupby
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING, Any, Callable, Generator, Sized

import pytest
from executing import Source

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

__all__ = ('insert_assert',)


@dataclass
class ToReplace:
    file: Path
    start_line: int
    end_line: int
    code: str


to_replace: list[ToReplace] = []
insert_assert_calls: ContextVar[int] = ContextVar('insert_assert_calls', default=0)
insert_assert_print: ContextVar[bool] = ContextVar('insert_assert_print')
insert_assert_enabled: ContextVar[bool] = ContextVar('insert_assert_enabled')


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        '--insert-assert-print',
        action='store_true',
        default=False,
        help='Print statements that would be substituted for insert_assert(), instead of writing to files',
    )
    parser.addoption(
        '--insert-assert-fail',
        action='store_true',
        default=False,
        help='Fail tests which include one or more insert_assert() calls',
    )
    parser.addoption(
        '--insert-assert-enable',
        dest='insert_assert_enabled',
        action='store_true',
        default=None,
        help='Enable insert_assert() calls, default is enabled unless "CI" environment variable is set',
    )
    parser.addoption(
        '--insert-assert-disable',
        dest='insert_assert_enabled',
        action='store_false',
        default=None,
        help='Disable insert_assert() calls, default is enabled unless "CI" environment variable is set',
    )


@pytest.fixture(scope='session', autouse=True)
def insert_assert_add_to_builtins(request: SubRequest) -> None:
    insert_assert_print.set(request.config.getoption('insert_assert_print'))
    as_enabled = request.config.getoption('insert_assert_enabled')
    if as_enabled is None:
        as_enabled = not bool(os.getenv('CI'))
    insert_assert_enabled.set(as_enabled)
    __builtins__['insert_assert'] = insert_assert


@pytest.fixture(autouse=True)
def insert_assert_maybe_fail(request: SubRequest) -> Generator[None, None, None]:
    if not request.config.getoption('insert_assert_fail'):
        yield
    else:
        insert_assert_calls.set(0)
        yield
        count = insert_assert_calls.get()
        if count:
            pytest.fail(f'{count} insert_assert() call{plural(count)}, failing due to --insert-assert-fail option')


def pytest_terminal_summary() -> None:
    if to_replace:
        # TODO replace with a pytest argument
        print_instead = insert_assert_print.get()

        highlight = None
        if print_instead:
            highlight = get_pygments()

        files = 0
        for file, group in groupby(to_replace, key=lambda tr: tr.file):
            # we have to substitute lines in reverse order to avoid messing up line numbers
            lines = file.read_text().splitlines()
            for tr in sorted(group, key=lambda x: x.start_line, reverse=True):
                if print_instead:
                    hr = '-' * 80
                    code = highlight(tr.code) if highlight else tr.code
                    print(f'{file} - {tr.start_line}:{tr.end_line}:\n{hr}\n{code}{hr}\n')
                else:
                    lines[tr.start_line - 1 : tr.end_line] = tr.code.splitlines()
            if not print_instead:
                file.write_text('\n'.join(lines))
            files += 1
        print(f'Replaced {len(to_replace)} insert_assert() call{plural(to_replace)} in {files} file{plural(files)}')


def insert_assert(value: Any) -> None:
    if not insert_assert_enabled.get():
        raise RuntimeError('insert_assert() is disabled, either due to --insert-assert-disable or "CI" env var')
    call_frame: FrameType = sys._getframe(1)

    source = Source.for_frame(call_frame)
    ex = source.executing(call_frame)
    ast_arg = ex.node.args[0]
    if isinstance(ast_arg, ast.Name):
        arg = ast_arg.id
    else:
        arg = ' '.join(map(str.strip, ex.source.asttokens().get_text(ast_arg).splitlines()))

    python_code = f'# insert_assert({arg})\nassert {arg} == {custom_repr(value)}'

    format_code = load_black()
    if format_code:
        python_code = format_code(python_code)

    python_code = textwrap.indent(python_code, ex.node.col_offset * ' ')
    to_replace.append(ToReplace(Path(call_frame.f_code.co_filename), ex.node.lineno, ex.node.end_lineno, python_code))
    insert_assert_calls.set(insert_assert_calls.get() + 1)


def custom_repr(value: Any) -> Any:
    if isinstance(value, (list, tuple, set, frozenset)):
        return value.__class__(map(custom_repr, value))
    elif isinstance(value, dict):
        return value.__class__((custom_repr(k), custom_repr(v)) for k, v in value.items())
    if isinstance(value, Enum):
        return PlainRepr(f'{value.__class__.__name__}.{value.name}')
    else:
        return PlainRepr(repr(value))


class PlainRepr:
    __slots__ = ('s',)

    def __init__(self, s: str):
        self.s = s

    def __repr__(self) -> str:
        return self.s


def plural(v: int | Sized) -> str:
    if isinstance(v, (int, float)):
        n = v
    else:
        n = len(v)
    return '' if n == 1 else 's'


@lru_cache
def load_black() -> Callable[[str], str] | None:  # noqa: C901
    """
    Build black configuration from "pyproject.toml".

    Black doesn't have a nice self-contained API for reading pyproject.toml, hence all this.
    """
    try:
        from black import format_file_contents
        from black.files import find_pyproject_toml, parse_pyproject_toml
        from black.mode import Mode, TargetVersion
        from black.parsing import InvalidInput
    except ImportError:
        return None

    def convert_target_version(target_version_config: Any) -> set[Any] | None:
        if target_version_config is not None:
            return None
        elif not isinstance(target_version_config, list):
            raise ValueError('Config key "target_version" must be a list')
        else:
            return {TargetVersion[tv.upper()] for tv in target_version_config}

    @dataclass
    class ConfigArg:
        config_name: str
        keyword_name: str
        converter: Callable[[Any], Any]

    config_mapping: list[ConfigArg] = [
        ConfigArg('target_version', 'target_versions', convert_target_version),
        ConfigArg('line_length', 'line_length', int),
        ConfigArg('skip_string_normalization', 'string_normalization', lambda x: not x),
        ConfigArg('skip_magic_trailing_commas', 'magic_trailing_comma', lambda x: not x),
    ]

    config_str = find_pyproject_toml((str(Path.cwd()),))
    mode_ = None
    fast = False
    if config_str:
        try:
            config = parse_pyproject_toml(config_str)
        except (OSError, ValueError) as e:
            raise ValueError(f'Error reading configuration file: {e}')

        if config:
            kwargs = dict()
            for config_arg in config_mapping:
                try:
                    value = config[config_arg.config_name]
                except KeyError:
                    pass
                else:
                    kwargs[config_arg.keyword_name] = config_arg.converter(value)

            mode_ = Mode(**kwargs)
            fast = bool(config.get('fast'))

    mode = mode_ or Mode()

    def format_code(code: str) -> str:
        try:
            return format_file_contents(code, fast=fast, mode=mode)
        except InvalidInput as e:
            print('black error, you will need to format the code manually,', e)
            return code

    return format_code


@lru_cache
def get_pygments() -> Callable[[str], str] | None:
    try:
        import pygments
        from pygments.formatters import Terminal256Formatter
        from pygments.lexers import PythonLexer
    except ImportError:  # pragma: no cover
        return None
    else:
        pyg_lexer, terminal_formatter = PythonLexer(), Terminal256Formatter()

        def highlight(code: str) -> str:
            return pygments.highlight(code, lexer=pyg_lexer, formatter=terminal_formatter)

        return highlight
