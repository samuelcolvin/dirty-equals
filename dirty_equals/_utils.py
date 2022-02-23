__all__ = 'plain_repr', 'PlainRepr', 'Omit'


class PlainRepr:
    def __init__(self, v: str):
        self.v = v

    def __repr__(self) -> str:
        return self.v


# used to omit arguments from repr
Omit = object()


def plain_repr(v: str) -> PlainRepr:
    return PlainRepr(v)
