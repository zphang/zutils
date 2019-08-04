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


def group_by(ls, key_func):
    result = {}
    for elem in ls:
        key = key_func(elem)
        if key not in result:
            result[key] = []
        result[key].append(elem)
    return result


def combine_dicts(dict_ls, strict=True, dict_class=dict):
    new_dict = dict_class()
    for i, dictionary in enumerate(dict_ls):
        for k, v in dictionary.items():
            if strict:
                if k in new_dict:
                    raise RuntimeError(f"repeated key {k} seen in dict {i}")
            new_dict[k] = v
    return new_dict
