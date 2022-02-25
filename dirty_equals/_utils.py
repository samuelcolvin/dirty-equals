__all__ = 'plain_repr', 'PlainRepr', 'Omit', 'NotGivenType', 'NotGiven'


class PlainRepr:
    """
    Hack to allow repr of string without quotes.
    """

    def __init__(self, v: str):
        self.v = v

    def __repr__(self) -> str:
        return self.v


def plain_repr(v: str) -> PlainRepr:
    return PlainRepr(v)


# used to omit arguments from repr
Omit = object()


class NotGivenType:
    """
    General type to represent omitted arguments while keeping mypy happy
    """


NotGiven = NotGivenType()
