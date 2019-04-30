from typing import Any, Union


def getter(attr_name: Any):
    def f(obj):
        return getattr(obj, attr_name)
    return f


def indexer(key):
    def f(obj):
        return obj[key]
    return f
