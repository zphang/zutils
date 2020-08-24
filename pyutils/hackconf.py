import os

import pyutils.io as io
import pyutils.datastructures as datastructures


class _DummyDefault:
    pass


def print_hack(msg):
    print(msg)


class Registry:
    def __init__(self, data=None, verbose=True):
        self.data = {} if data is None else data
        self.verbose = verbose
        self.verbose_get_shown = set()

    def get_item(self, key, default=_DummyDefault):
        if key in self.data:
            value = self.data[key]
            from_default = False
        else:
            if default is _DummyDefault:
                raise KeyError(f"Key '{key}' not found and no default provided")
            value = default
            from_default = True
        if self.verbose and key not in self.verbose_get_shown:
            if from_default:
                print_hack(f"[HACKCONF] Getting: '{key}' -> '{value}' (from default)")
            else:
                print_hack(f"[HACKCONF] Getting: '{key}' -> '{value}'")
            self.verbose_get_shown.add(key)
        return value

    def set_item(self, key, value):
        if self.verbose:
            print_hack(f"[HACKCONF] Setting: '{key}' -> '{value}'")
        self.data[key] = value

    @classmethod
    def load_from_json(cls, path, verbose=True):
        data = io.read_json(path)
        return cls(data=data, verbose=verbose)

    def to_dict(self):
        if self.data:
            return {k: v for k, v in self.data.items()}
        else:
            return {}


def get_item(key, default=_DummyDefault):
    global GLOBAL_REGISTRY
    return GLOBAL_REGISTRY.get_item(key=key, default=default)


def set_item(key, value):
    global GLOBAL_REGISTRY
    GLOBAL_REGISTRY.set_item(key=key, value=value)


def load_from_json(path, verbose=True):
    global GLOBAL_REGISTRY
    if verbose:
        print_hack(f"[HACKCONF] Loading global registry from: {path}")
    GLOBAL_REGISTRY = Registry.load_from_json(path=path, verbose=verbose)


def load_from_jsons(path_str, verbose=True):
    global GLOBAL_REGISTRY
    path_ls = path_str.split(",")
    if verbose:
        print_hack("[HACKCONF] Loading global registry from:")
        for path in path_ls:
            print("   ", path_ls)
    data = datastructures.combine_dicts([
        io.read_json(path)
        for path in path_ls
    ])
    GLOBAL_REGISTRY = Registry(data=data, verbose=verbose)


def to_dict():
    global GLOBAL_REGISTRY
    return GLOBAL_REGISTRY.to_dict()


OS_VERBOSE_GET_SHOWN = set()


def get_item_env(key, default=_DummyDefault, verbose=True):
    used_key = f"HACKCONF_{key}"
    if used_key in os.environ:
        value = os.environ[used_key]
        from_default = False
    elif default is not _DummyDefault:
        value = default
        from_default = True
    else:
        raise KeyError(f"Key '{key} ({used_key})' not found and no default provided")

    if verbose and key not in OS_VERBOSE_GET_SHOWN:
        if from_default:
            print_hack(f"[HACKCONF/os] Getting: '{key} ({used_key})' -> '{value}' (from_default)")
        else:
            print_hack(f"[HACKCONF/os] Getting: '{key} ({used_key})' -> '{value}'")
        OS_VERBOSE_GET_SHOWN.add(key)

    return value


def set_item_env(key, value):
    used_key = f"HACKCONF_{key}"
    os.environ[used_key] = value
    print_hack(f"[HACKCONF/os] Setting: '{key} ({used_key})' -> '{value}'")


GLOBAL_REGISTRY = Registry()
