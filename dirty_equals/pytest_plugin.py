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
from typing import TYPE_CHECKING, Any, Callable, Generator, Mapping, Optional, Sized

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


class PlainRepr:
    def __init__(self, value: Any) -> None:
        self._val = value

    def __repr__(self) -> str:
        if isinstance(self._val, Enum):
            return f'{self._val.__class__.__name__}.{self._val.name}'
        else:
            return repr(self._val)

    def __hash__(self) -> int:
        return hash(self._val)

    def __eq__(self, __o: object) -> bool:
        return self._val == __o


def apply_repl(selector: str, value: Any, current: Any) -> Any:
    if not selector:
        assert isinstance(current, PlainRepr)
        return PlainRepr(value)
    if selector[0] == "[":
        piece_end = selector.find("]")
        if piece_end == -1:
            # TODO: make all of these errors look like Invalid selector '["foo"]>["bar<["baz"]' or something nice
            raise ValueError("Invalid selector")
        piece = selector[: piece_end + 1]
        if '"' in piece or "'" in piece:
            # ["key"] or ['key']
            quote = piece[1]
            if len(piece) < 4 or piece[-2:] != f"{quote}]":
                raise ValueError("Invalid selector")
            key = piece[2:-2]
            current[key] = apply_repl(selector[piece_end + 1 :], value, current[key])
            return current
        elif piece == "[]":
            # index into every item
            for idx in range(len(current)):
                current[idx] = apply_repl(selector[piece_end + 1 :], value, current=current[idx])
            return current
        elif ":" in piece:
            # [start?:end?]
            start, end = piece[1:-1].split(":")
            start = int(start) if start else 0
            end = int(end) if end else len(current)
            for idx in range(start, end):
                current[idx] = apply_repl(selector[piece_end + 1 :], value, current=current[idx])
            return current
        # TODO handle:
        # - [idx]
        # - .attr
        # - .* (every attribute)
        # - [*] (every key)
        raise NotImplementedError("Unable to parse selector")
    return


def insert_assert(value: Any, *, repl: Optional[Mapping[str, Any]] = None) -> int:
    call_frame: FrameType = sys._getframe(1)
    if sys.version_info < (3, 8):  # pragma: no cover
        raise RuntimeError('insert_assert() requires Python 3.8+')
    if not insert_assert_enabled.get():
        raise RuntimeError('insert_assert() is disabled, either due to --insert-assert-disable or "CI" env var')

    format_code = load_black()
    ex = Source.for_frame(call_frame).executing(call_frame)
    if ex.node is None:  # pragma: no cover
        python_code = format_code(str(custom_repr(value)))
        raise RuntimeError(
            f'insert_assert() was unable to find the frame from which it was called, called with:\n{python_code}'
        )
    ast_arg = ex.node.args[0]
    if isinstance(ast_arg, ast.Name):
        arg = ast_arg.id
    else:
        arg = ' '.join(map(str.strip, ex.source.asttokens().get_text(ast_arg).splitlines()))
    repl_kwarg = next((kw for kw in ex.node.keywords if kw.arg == "repl"), None)
    if isinstance(repl_kwarg, ast.Name):
        repl_repr = repl_kwarg.id
    elif repl_kwarg is not None:
        repl_repr = ' '.join(map(str.strip, ex.source.asttokens().get_text(repl_kwarg).splitlines()))
    else:
        repl_repr = ""

    params = ", ".join((p for p in (arg, repl_repr) if p))

    expected_val_repr_template = custom_repr(value)

    if repl:
        for selector, value in repl.items():
            expected_val_repr_template = apply_repl(selector, value, expected_val_repr_template)

    python_code = format_code(f'# insert_assert({params})\nassert {arg} == {expected_val_repr_template}')

    python_code = textwrap.indent(python_code, ex.node.col_offset * ' ')
    to_replace.append(ToReplace(Path(call_frame.f_code.co_filename), ex.node.lineno, ex.node.end_lineno, python_code))
    calls = insert_assert_calls.get() + 1
    insert_assert_calls.set(calls)
    return calls


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
    if as_enabled:
        try:
            __builtins__['insert_assert'] = insert_assert
        except TypeError:
            # happens on pypy
            pass


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


@pytest.fixture(name='insert_assert')
def insert_assert_fixture() -> Callable[[Any], int]:
    if not insert_assert_enabled.get():
        pytest.fail('insert_assert() is disabled, either due to --insert-assert-disable or "CI" env var')
    else:
        return insert_assert


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
                    line_no = f'{tr.start_line}' if tr.start_line == tr.end_line else f'{tr.start_line}-{tr.end_line}'
                    print(f'{file} - {line_no}:\n{hr}\n{code}{hr}\n')
                else:
                    lines[tr.start_line - 1 : tr.end_line] = tr.code.splitlines()
            if not print_instead:
                file.write_text('\n'.join(lines))
            files += 1
        prefix = 'Printed' if print_instead else 'Replaced'
        print(f'{prefix} {len(to_replace)} insert_assert() call{plural(to_replace)} in {files} file{plural(files)}')
        to_replace.clear()


def custom_repr(value: Any) -> Any:
    if isinstance(value, (list, tuple, set, frozenset)):
        return value.__class__(map(custom_repr, value))
    elif isinstance(value, dict):
        return value.__class__((custom_repr(k), custom_repr(v)) for k, v in value.items())
    return PlainRepr(value)


def plural(v: int | Sized) -> str:
    if isinstance(v, (int, float)):
        n = v
    else:
        n = len(v)
    return '' if n == 1 else 's'


@lru_cache(maxsize=None)
def load_black() -> Callable[[str], str]:  # noqa: C901
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
        return lambda x: x

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
                    value = config_arg.converter(value)
                    if value is not None:
                        kwargs[config_arg.keyword_name] = value

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


@lru_cache(maxsize=None)
def get_pygments() -> Callable[[str], str] | None:  # pragma: no cover
    if not isatty():
        return None
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


def isatty() -> bool:
    stream = sys.stdout
    try:
        return stream.isatty()
    except Exception:
        return False
