import pyutils


def test_list_equal():
    assert pyutils.list_equal([1], [1])
    assert not pyutils.list_equal([1], [2])
    assert not pyutils.list_equal([1], [1, 2])


def test_dict_equal():
    assert pyutils.dict_equal({1: 2}, {1: 2})
    assert not pyutils.dict_equal({1: 2}, {1: 3})
    assert not pyutils.dict_equal({1: 2}, {2: 2})
    assert not pyutils.dict_equal({1: 2}, {2: 2, 1: 1})
