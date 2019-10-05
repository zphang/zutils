import argparse
import attr
import copy as copylib
import inspect
import json
import sys
import pathlib

from pyutils.io import read_json
from pyutils.datastructures import combine_dicts


def _is_true(x):
    return x == "True"


def argparse_attr(default=attr.NOTHING, validator=None,
                  repr=True, cmp=True, hash=True, init=True,
                  converter=None, opt_string=None,
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
        converter=converter,
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


def read_parser(parser, class_with_attributes, skip_non_class_attributes=None, args=None):
    attribute_name_set = {
        attribute.name
        for attribute in class_with_attributes.__attrs_attrs__
    }

    kwargs = dict()
    leftover_kwargs = dict()

    for k, v in vars(parser.parse_args(args)).items():
        if k in attribute_name_set:
            kwargs[k] = v
        else:
            if skip_non_class_attributes is not None and k not in skip_non_class_attributes:
                raise RuntimeError(f"Unknown attribute {k}")
            leftover_kwargs[k] = v

    instance = class_with_attributes(**kwargs)
    if skip_non_class_attributes:
        return instance, leftover_kwargs
    else:
        return instance


# === Methods === #

# == Class Methods
def run_cli(cls, args=None, prog=None, description=None):
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
        args=args,
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


class RunConfig:
    @classmethod
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

    @classmethod
    def run_cli_json_prepend(cls, cl_args=None, prog=None, description=None):
        # Prototype
        # Assumptions: no positional?
        parser = argparse.ArgumentParser(
            prog=prog,
            description=description,
        )
        parser.add_argument("--ZZsrc", type=str, action='append')
        parser.add_argument("--ZZoverrides", type=str, nargs="+")
        pre_args, _ = parser.parse_known_args(cl_args)
        if cl_args is None:
            cl_args = sys.argv[1:]
        if pre_args.ZZsrc is not None:
            imported_dict_ls = [
                read_json(path)
                for path in pre_args.ZZsrc
            ]
            combined_imported_dict = combine_dicts(imported_dict_ls, strict=True)
            if pre_args.ZZoverrides is not None:
                overrides = [f"--{k}" for k in pre_args.ZZoverrides]
            else:
                overrides = []

            added_args = []
            for k, v in combined_imported_dict.items():
                formatted_k = f"--{k}"
                if formatted_k in cl_args and formatted_k not in overrides:
                    raise RuntimeError(f"Attempting to override {formatted_k}")
                added_args.append(formatted_k)
                added_args.append(str(v))
            submitted_args = added_args + cl_args
        else:
            assert pre_args.ZZoverrides is None
            submitted_args = cl_args
        update_parser(
            parser=parser,
            class_with_attributes=cls,
        )
        result, _ = read_parser(
            parser=parser,
            class_with_attributes=cls,
            skip_non_class_attributes=["ZZsrc", "ZZoverrides"],
            args=submitted_args,
        )
        assert isinstance(result, cls)
        return result

    @classmethod
    def from_json(cls, json_string):
        return cls(**json.loads(json_string))

    @classmethod
    def from_json_path(cls, json_path):
        with open(json_path, "r") as f:
            return cls.from_json(f.read())

    @classmethod
    def from_json_arg(cls):
        assert len(sys.argv) == 2
        return cls.from_json_path(sys.argv[1])

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

    def copy(self):
        return copylib.deepcopy(self)

    def _post_init(self):
        pass

    def __attrs_post_init__(self):
        self._post_init()


# === Definition === #
def run_config(cls):
    cls = attr.s(cls)

    if not isinstance(cls, RunConfig):
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
