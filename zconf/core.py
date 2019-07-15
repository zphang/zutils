import argparse
import attr
import copy as copylib
import inspect
import json
import sys
import pathlib


def _is_true(x):
    return x == "True"


def argparse_attr(default=attr.NOTHING, validator=None,
                  repr=True, cmp=True, hash=True, init=True,
                  convert=None, opt_string=None,
                  **argparse_kwargs):
    if opt_string is None:
        opt_string_ls = []
    elif isinstance(opt_string, str):
        opt_string_ls = [opt_string]
    else:
        opt_string_ls = opt_string

    if argparse_kwargs.get("type", None) is bool:
        argparse_kwargs["choices"] = {True, False}
        argparse_kwargs["type"] = _is_true

    if argparse_kwargs.get("action", None) == "store_true":
        default = False

    return attr.attr(
        default=default,
        validator=validator,
        repr=repr,
        cmp=cmp,
        hash=hash,
        init=init,
        convert=convert,
        metadata={
            "opt_string_ls": opt_string_ls,
            "argparse_kwargs": argparse_kwargs,
        },
        kw_only=True,
    )


def update_parser(parser, class_with_attributes):
    for attribute in class_with_attributes.__attrs_attrs__:
        if "argparse_kwargs" in attribute.metadata:
            argparse_kwargs = attribute.metadata["argparse_kwargs"]
            opt_string_ls = attribute.metadata["opt_string_ls"]
            is_positional = "nargs" in argparse_kwargs  # TODO: get better criteria
            if not is_positional:
                if attribute.default is attr.NOTHING:
                    argparse_kwargs = argparse_kwargs.copy()
                    argparse_kwargs["required"] = True
                else:
                    argparse_kwargs["default"] = attribute.default
            if is_positional:
                argparse_arg_name = attribute.name
            else:
                argparse_arg_name = f"--{attribute.name}"

            parser.add_argument(
                argparse_arg_name, *opt_string_ls,
                **argparse_kwargs
            )


def read_parser(parser, class_with_attributes, skip_non_class_attributes=False):
    attribute_name_set = {
        attribute.name
        for attribute in class_with_attributes.__attrs_attrs__
    }

    kwargs = dict()
    leftover_kwargs = dict()

    for k, v in vars(parser.parse_args()).items():
        if k in attribute_name_set:
            kwargs[k] = v
        else:
            if not skip_non_class_attributes:
                raise RuntimeError(f"Unknown attribute {k}")
            leftover_kwargs[k] = v

    instance = class_with_attributes(**kwargs)
    if skip_non_class_attributes:
        return instance, leftover_kwargs
    else:
        return instance


# === Methods === #

# == Class Methods
def run_cli(cls, prog=None, description=None):
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
    )
    update_parser(
        parser=parser,
        class_with_attributes=cls,
    )
    result = read_parser(
        parser=parser,
        class_with_attributes=cls,
    )
    assert isinstance(result, cls)
    return result


def from_json(cls, json_string):
    return cls(**json.loads(json_string))


def from_json_path(cls, json_path):
    with open(json_path, "r") as f:
        return cls.from_json(f.read())


def from_json_arg(cls):
    assert len(sys.argv) == 2
    return cls.from_json_path(sys.argv[1])


# == Instance Methods
def to_dict(self):
    config_dict = {}
    for attribute in inspect.getfullargspec(self.__class__).kwonlyargs:
        config_dict[attribute] = getattr(self, attribute)
    return config_dict


def to_json(self):
    serialized_dict = self.to_dict()
    for key, val in serialized_dict.items():
        if isinstance(val, pathlib.Path):
            serialized_dict[key] = str(val)
    return json.dumps(serialized_dict, indent=2)


def _inst_copy(self):
    return copylib.deepcopy(self)


# === Definition === #
def run_config(cls):
    cls = attr.s(cls)

    # Class methods
    cls.run_cli = classmethod(run_cli)
    cls.from_json = classmethod(from_json)
    cls.from_json_path = classmethod(from_json_path)
    cls.from_json_arg = classmethod(from_json_arg)

    # Instance methods
    cls.to_dict = to_dict
    cls.to_json = to_json
    cls.copy = _inst_copy

    return cls
