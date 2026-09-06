def test_anything_diff(pytester):
    # see https://github.com/samuelcolvin/dirty-equals/issues/108
    pytester.makepyfile("""
from dirty_equals import AnyThing

def test_dirty_equals_1():
    leftdct = {"id": 1, "name": "AAA", "anything": [1, 2, 3]}
    rightdct = {"id": 1, "name": "BBB", "anything": AnyThing()}
    assert leftdct == rightdct
""")
    result = pytester.runpytest('-vv')

    assert [line for line in result.outlines if line.startswith('E ')] == [
        "E       AssertionError: assert {'id': 1, 'name': 'AAA', 'anything': [1, "
        "2, 3]} == {'id': 1, 'name': 'BBB', 'anything': AnyThing()}",
        'E         ',
        'E         Common items:',
        "E         {'anything': [1, 2, 3], 'id': 1}",
        'E         Differing items:',
        "E         {'name': 'AAA'} != {'name': 'BBB'}",
        'E         ',
        'E         Full diff:',
        'E           {',
        "E               'anything': [",
        'E                   1,',
        'E                   2,',
        'E                   3,',
        'E               ],',
        "E               'id': 1,",
        "E         -     'name': 'BBB',",
        'E         ?              ^^^',
        "E         +     'name': 'AAA',",
        'E         ?              ^^^',
        'E           }',
    ]


def test_islist_diff(pytester):
    # see https://github.com/samuelcolvin/dirty-equals/issues/73
    pytester.makepyfile("""
from dirty_equals import IsList

def test():
    actions = [
        "ddsdsdads ",
        "sfafsdsd",
        "dfds sdfsef",
        "sfdssdf ",
        "sdsadfs",
        "dsfsdfsd",
        "cfdfdfd",
        "dgffgfdgfd",
        "fdsfsdgfsdgsf",
    ]
    assert (actions, 1, 2, 3) == (
        IsList(length=...),
        1,
        2,
        0,
    )
""")

    result = pytester.runpytest('-vv')

    assert [line for line in result.outlines if line.startswith('E ')] == [
        "E       AssertionError: assert (['ddsdsdads ', 'sfafsdsd', 'dfds sdfsef', "
        "'sfdssdf ', 'sdsadfs', 'dsfsdfsd', 'cfdfdfd', 'dgffgfdgfd', "
        "'fdsfsdgfsdgsf'], 1, 2, 3) == (['ddsdsdads ', 'sfafsdsd', 'dfds sdfsef', "
        "'sfdssdf ', 'sdsadfs', 'dsfsdfsd', 'cfdfdfd', 'dgffgfdgfd', "
        "'fdsfsdgfsdgsf'], 1, 2, 0)",
        'E         ',
        'E         At index 3 diff: 3 != 0',
        'E         ',
        'E         Full diff:',
        'E           (',
        'E               [',
        "E                   'ddsdsdads ',",
        "E                   'sfafsdsd',",
        "E                   'dfds sdfsef',",
        "E                   'sfdssdf ',",
        "E                   'sdsadfs',",
        "E                   'dsfsdfsd',",
        "E                   'cfdfdfd',",
        "E                   'dgffgfdgfd',",
        "E                   'fdsfsdgfsdgsf',",
        'E               ],',
        'E               1,',
        'E               2,',
        'E         -     0,',
        'E         ?     ^',
        'E         +     3,',
        'E         ?     ^',
        'E           )',
    ]
