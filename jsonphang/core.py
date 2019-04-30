import json
import os

from typing import Dict, Sequence

from pyutils import chain_idx_get


class KEYS:
    META = "###-META-###"
    INCLUDE = "INCLUDE"
    ENV_STRICT = "ENV_STRICT"
    GRANULAR_COMBINE = "GRANULAR_COMBINE"


class CONSTANTS:
    ENV_HEAD = "#ENV("
    ENV_TAIL = ")ENV#"


class DEFAULTS:
    ENV_STRICT = False
    ENV_DEFAULT = None
    GRANULAR_COMBINE = False


def read_json(path: str) -> Dict:
    with open(path, "r") as f:
        return json.loads(f.read())


def write_json(data: Dict, path: str):
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=2))


def smart_load(path):
    conf = read_json(path)
    conf = process_includes(conf)


def process_env_variables(conf: Dict) -> Dict:
    do_strict_env = chain_idx_get(
        container=conf,
        key_list=[KEYS.META, KEYS.ENV_STRICT],
        default=DEFAULTS.ENV_STRICT,
    )
    conf = conf.copy()
    return _recursive_process_env_variables(conf, do_strict_env=do_strict_env)


def _recursive_process_env_variables(conf, do_strict_env):
    for k, v in conf:
        if isinstance(v, dict):
            _recursive_process_env_variables(v, do_strict_env=do_strict_env)

        elif isinstance(v, str):
            if v.startswith(CONSTANTS.ENV_HEAD) and v.endswith(CONSTANTS.ENV_TAIL):
                env_key = v[len(CONSTANTS.ENV_HEAD):len(CONSTANTS.ENV_TAIL)]
                if env_key in os.environ:
                    conf[k] = os.environ[env_key]
                else:
                    if do_strict_env:
                        raise RuntimeError(f"Can't find environment variable {env_key}")
                    else:
                        conf[k] = DEFAULTS.ENV_DEFAULT


def process_includes(conf: Dict):
    try:
        include_list = conf[KEYS.META][KEYS.INCLUDE]
    except KeyError:
        return conf

    conf_list = [
        process_includes(read_json(path))
        for path in include_list
    ] + [conf]
    return combine_conf_list(conf_list)


def combine_conf_list(conf_list: Sequence):
    conf = conf_list[0]
    for next_conf in conf_list[1:]:
        conf = combine_two_dicts(conf, next_conf)
    return conf


def combine_two_dicts(conf_a: Dict, conf_b: Dict) -> Dict:
    conf = conf_a.copy()
    for k, b_elem in conf_b.items():
        if k not in conf_a:
            conf[k] = b_elem
            continue

        a_elem = conf[k]
        if not isinstance(a_elem, dict):
            conf[k] = b_elem
            continue

        # Note: GRANULAR_COMBINE is in the b_dict
        do_granular_combine = chain_idx_get(
            dictionary=b_elem,
            key_list=[KEYS.META, KEYS.GRANULAR_COMBINE],
            default=DEFAULTS.GRANULAR_COMBINE,
        )
        if do_granular_combine:
            conf[k] = combine_two_dicts(a_elem, b_elem)
        else:
            conf[k] = b_elem
    return conf

