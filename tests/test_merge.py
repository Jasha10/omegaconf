import pytest

from omegaconf import OmegaConf, Config, nodes


def test_dict_merge_1():
    a = OmegaConf.create({})
    b = OmegaConf.create({'a': 1})
    c = Config.map_merge(a, b)
    assert b == c


def test_dict_merge_no_modify():
    # Test that map_merge does not modify the input
    a = OmegaConf.create({})
    b = OmegaConf.create({'a': 1})
    Config.map_merge(a, b)
    assert a == {}
    assert b == {'a': 1}


def test_dict_merge_2():
    a = OmegaConf.create({'a': 1})
    b = OmegaConf.create({'b': 2})
    c = Config.map_merge(a, b)
    assert {'a': 1, 'b': 2} == c


def test_dict_merge_3():
    a = OmegaConf.create({'a': {'a1': 1, 'a2': 2}})
    b = OmegaConf.create({'a': {'a1': 2}})
    c = Config.map_merge(a, b)
    assert {'a': {'a1': 2, 'a2': 2}} == c


@pytest.mark.parametrize('inputs, expected', [
    # dictionaries
    ((dict(a=None), dict(b=None)), dict(a=None, b=None)),
    ((dict(a=1, b=2), dict(b=3)), dict(a=1, b=3)),
    ((dict(a=1, b=2), dict(b=dict(c=3))), dict(a=1, b=dict(c=3))),
    ((dict(b=dict(c=1)), dict(b=1)), dict(b=1)),
    ((dict(list=[1, 2, 3]), dict(list=[4, 5, 6])), dict(list=[4, 5, 6])),
    ((dict(a=1), dict(a=nodes.IntegerNode(10))), dict(a=10)),
    ((dict(a=1), dict(a=nodes.IntegerNode(10))), dict(a=nodes.IntegerNode(10))),
    ((dict(a=nodes.IntegerNode(10)), dict(a=1)), dict(a=1)),
    ((dict(a=nodes.IntegerNode(10)), dict(a=1)), dict(a=nodes.IntegerNode(1))),
    # lists
    (([1, 2, 3], [4, 5, 6]), [4, 5, 6]),
    (([[1, 2, 3]], [[4, 5, 6]]), [[4, 5, 6]]),
    (([1, 2, dict(a=10)], [4, 5, dict(b=20)]), [4, 5, dict(b=20)]),
    # Interpolations
    ((dict(data=123, reference='${data}'), dict(data=456)), dict(data=456, reference=456)),
    ((dict(missing='${data}'), dict(missing=123)), dict(missing=123)),
    ((dict(missing=123), dict(missing='${data}'), dict(missing=456)), dict(missing=456)),
])
def test_merge(inputs, expected):
    configs = [OmegaConf.create(c) for c in inputs]
    assert OmegaConf.merge(*configs) == expected


# like above but don't verify merge does not change because even eq does not work no tuples because we convert
# them to a list
@pytest.mark.parametrize('a_, b_, expected', [
    ((1, 2, 3), (4, 5, 6), [4, 5, 6]),
])
def test_merge_no_eq_verify(a_, b_, expected):
    a = OmegaConf.create(a_)
    b = OmegaConf.create(b_)
    c = OmegaConf.merge(a, b)
    # verify merge result is expected
    assert expected == c


def test_merge_with_1():
    a = OmegaConf.create()
    b = OmegaConf.create(dict(a=1, b=2))
    a.merge_with(b)
    assert a == b


def test_merge_with_2():
    a = OmegaConf.create()
    a.inner = {}
    b = OmegaConf.create('''
    a : 1
    b : 2
    ''')
    a.inner.merge_with(b)
    assert a.inner == b


def test_3way_dict_merge():
    c1 = OmegaConf.create('{a: 1, b: 2}')
    c2 = OmegaConf.create('{b: 3}')
    c3 = OmegaConf.create('{a: 2, c: 3}')
    c4 = OmegaConf.merge(c1, c2, c3)
    assert {'a': 2, 'b': 3, 'c': 3} == c4


def test_merge_list_list():
    a = OmegaConf.create([1, 2, 3])
    b = OmegaConf.create([4, 5, 6])
    a.merge_with(b)
    assert a == b


def test_merge_list_list__deprecated():
    a = OmegaConf.create([1, 2, 3])
    b = OmegaConf.create([4, 5, 6])
    a.merge_from(b)
    assert a == b


@pytest.mark.parametrize('base, merge, exception', [
    ({}, [], TypeError),
    ([], {}, TypeError),
    ([1, 2, 3], None, ValueError),
    (dict(a=10), None, ValueError),
])
def test_merge_error(base, merge, exception):
    base = OmegaConf.create(base)
    merge = None if merge is None else OmegaConf.create(merge)
    with pytest.raises(exception):
        OmegaConf.merge(base, merge)