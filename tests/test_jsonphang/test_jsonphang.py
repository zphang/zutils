import jsonphang


def test_chain_idx():
    d = {1: {2: 3}}
    assert jsonphang.chain_idx(d, [1, 2]) == 3
