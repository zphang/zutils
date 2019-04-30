import pytest

import pyutils


def test_indexer():
    assert pyutils.indexer(1)({1: 2}) == 2
    with pytest.raises(KeyError):
        pyutils.indexer("1")({1: 2})
