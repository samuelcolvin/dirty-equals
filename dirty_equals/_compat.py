import sys

if sys.version_info[:2] >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal, Protocol

if sys.version_info[:2] >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

__all__ = ['Literal', 'Protocol', 'TypeAlias']
