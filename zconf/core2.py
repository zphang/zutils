from dataclasses import dataclass
from typing import TypeVar, Sequence

T = TypeVar('T')


class MyClass:
    pass

    def hi(self):
        pass


def go(x: T) -> T:
    return [x, "2"]


go(MyClass()).hiw()
