import argparse
import os
import subprocess

from pyutils.io import read_json

ZSYNC_CONF_FILE_NAME = ".zsync.json"
ZSYNC_BASE_PATH_ENV_NAME = "ZSYNC_BASE_PATH"


def get_global_base_path():
    if ZSYNC_BASE_PATH_ENV_NAME in os.environ:
        return os.environ[ZSYNC_BASE_PATH_ENV_NAME]
    else:
        return os.path.join(os.path.expanduser("~"), ".zsync")


def get_global_config():
    global_config_path = os.path.join(get_global_base_path(), "global.json")
    if os.path.exists(global_config_path):
        return read_json(global_config_path)
    else:
        return {}


def get_local_config(cwd):
    local_path = os.path.join(cwd, ZSYNC_CONF_FILE_NAME)
    if os.path.exists(local_path):
        return read_json(local_path)
    else:
        return {}


def load_config(location, verbose=True):
    cwd = os.getcwd()

    # 1. Local
    local_config = get_local_config(cwd)
    if location in local_config:
        if verbose:
            print("Loading from local")
        return local_config[location]

    # 2. Global
    global_config = get_global_config()
    if "paths" in global_config and cwd in global_config["paths"]:
        if verbose:
            print("Loading from global-paths")
        specific_config = read_json(os.path.join(get_global_base_path(), global_config["paths"][cwd]))
        return specific_config[location]

    if "configs" in global_config \
            and cwd in global_config["configs"]\
            and location in global_config["configs"][location]:
        if verbose:
            print("Loading from global-configs")
        return global_config["configs"][cwd][location]

    raise KeyError("'{}' config not found".format(location))


def construct_rsync_tokens(ssh_key_path, exclude_list, delete, src, dst):
    """
    s = "rsync \\\n"
    s += "    -avz -e 'ssh -i {}' \\\n".format(ssh_key_path)
    for exclude in exclude_list:
        s += "    --exclude='{}' \\\n".format(exclude)
    if delete:
        s += "    --delete \\\n"
    s += "{} {}".format(src, dst)
    return s
    """
    tokens = [
        "rsync",
        "-avz", "-e", "'ssh -i {}'".format(ssh_key_path),
    ]
    for exclude in exclude_list:
        tokens.append("--exclude='{}'".format(exclude))
    if delete:
        tokens.append("--delete")
    tokens.append(src)
    tokens.append(dst)
    return tokens


def perform_command(tokens, show):
    formatted_command = " \\\n    ".join(tokens)
    if show:
        print(formatted_command)
    else:
        result = subprocess.run(
            formatted_command,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
        )
        print(result.stdout.decode('utf-8'))


def zsync_to(location, show):
    location_config = load_config(location)
    src = location_config["local_path"]
    dst = "{}@{}:{}".format(
        location_config["remote_user"],
        location_config["remote_host"],
        os.path.split(location_config["remote_path"])[0],
    )
    tokens = construct_rsync_tokens(
        ssh_key_path=location_config["ssh_key_path"],
        exclude_list=location_config["exclude_list"],
        delete=location_config["delete"],
        src=src,
        dst=dst,
    )
    perform_command(tokens, show)


def zsync_from(location, show):
    location_config = load_config(location)
    src = "{}@{}:{}".format(
        location_config["remote_user"],
        location_config["remote_host"],
        location_config["remote_path"],
    )
    dst = os.path.split(location_config["local_path"])[0]
    tokens = construct_rsync_tokens(
        ssh_key_path=location_config["ssh_key_path"],
        exclude_list=location_config["exclude_list"],
        delete=location_config["delete"],
        src=src,
        dst=dst,
    )
    perform_command(tokens, show)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mode', help='to, from')
    parser.add_argument('location')
    parser.add_argument('--show', action="store_true")
    args = parser.parse_args()
    if args.mode == "to":
        zsync_to(
            location=args.location,
            show=args.show,
        )
    elif args.mode == "from":
        zsync_from(
            location=args.location,
            show=args.show,
        )
    else:
        raise KeyError(args.mode)


if __name__ == "__main__":
    main()
