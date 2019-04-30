from typing import Collection, Any, Sequence


def take_one(ls: Collection) -> Any:
    if not len(ls) == 1:
        raise IndexError(f"has more than one element ({len(ls)})")
    return next(iter(ls))


def chain_idx_get(container: Collection, key_list: Sequence, default: Any) -> Any:
    try:
        return chain_idx(container, key_list)
    except (KeyError, IndexError, TypeError):
        return default


def chain_idx(container: Collection, key_list: Sequence) -> Any:
    curr = container
    for key in key_list:
        curr = curr[key]
    return curr
