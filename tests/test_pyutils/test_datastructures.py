import pytest

import pyutils


def test_take_one():
    assert pyutils.take_one([9]) == 9
    assert pyutils.take_one((9,)) == 9
    assert pyutils.take_one({9}) == 9
    assert pyutils.take_one("9") == "9"
    assert pyutils.take_one({9: 10}) == 9

    with pytest.raises(IndexError):
        pyutils.take_one([])
    with pytest.raises(IndexError):
        pyutils.take_one([1, 2])
    with pytest.raises(IndexError):
        pyutils.take_one("2342134")


def test_chain_idx():
    # dict
    d = {1: {2: 3}}
    ls = [1, [2], [None, [3]]]
    assert pyutils.chain_idx(d[1], [2]) == 3
    assert pyutils.chain_idx(d, [1, 2]) == 3
    with pytest.raises(KeyError):
        pyutils.chain_idx(d, [1, 3])
    with pytest.raises(KeyError):
        pyutils.chain_idx(d, [3])

    # list
    assert pyutils.chain_idx(ls, [0]) == 1
    assert pyutils.list_equal(pyutils.chain_idx(ls, [1]), [2])
    assert pyutils.chain_idx(ls, [1, 0]) == 2
    assert pyutils.chain_idx(ls, [2, 0]) is None
    assert pyutils.chain_idx(ls, [2, 1, 0]) == 3
    with pytest.raises(TypeError):
        pyutils.chain_idx(ls, [0, 0, 0])
    with pytest.raises(IndexError):
        pyutils.chain_idx(ls, [1, 1])


def test_chain_idx_get():
    # dict
    d = {1: {2: 3}}
    ls = [1, [2], [None, [3]]]
    assert pyutils.chain_idx_get(d[1], [2], default=1234) == 3
    assert pyutils.chain_idx_get(d, [1, 3], default=1234) == 1234

    # list
    assert pyutils.chain_idx_get(ls, [0], default=1234) == 1
    assert pyutils.chain_idx_get(ls, [0, 0], default=1234) == 1234
    assert pyutils.chain_idx_get(ls, [1, 1], default=1234) == 1234


def test_partition_list():
    assert pyutils.list_equal(
        pyutils.partition_list(list(range(10)), 5),
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
    )
    assert pyutils.list_equal(
        pyutils.partition_list(list(range(10)), 3),
        [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]],
    )
    assert pyutils.list_equal(
        pyutils.partition_list(list(range(10)), 1),
        [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]],
    )
