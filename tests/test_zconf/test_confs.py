import pytest

from zconf import zconfig, BaseConfiguration, argparse_attr


@zconfig
class Config(BaseConfiguration):
    attr1 = argparse_attr(default=None)
    attr2 = argparse_attr(required=True)


def test_args():
    config = Config(attr1=1, attr2=2)
    assert config.attr1 == 1
    assert config.attr2 == 2

    config = Config(attr2=2)
    assert config.attr1 is None
    assert config.attr2 == 2


def test_args_required():
    with pytest.raises(TypeError):
        Config()
