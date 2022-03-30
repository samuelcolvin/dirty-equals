from typing import TYPE_CHECKING

__all__ = 'Protocol', 'Literal', 'TypeAlias'


if TYPE_CHECKING:
    # this weirdness is required to avoid issues with mkdocstrings[python]
    from typing import Literal, Protocol, TypeAlias
else:
    try:
        from typing import Literal, Protocol, TypeAlias
    except ImportError:
        from typing_extensions import Literal, Protocol, TypeAlias
