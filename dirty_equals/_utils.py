try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore[misc]

__all__ = 'plain_repr', 'PlainRepr', 'Omit', 'Literal'


class PlainRepr:
    def __init__(self, v: str):
        self.v = v

    def __repr__(self) -> str:
        return self.v


# used to omit arguments from repr
Omit = object()


def plain_repr(v: str) -> PlainRepr:
    return PlainRepr(v)
