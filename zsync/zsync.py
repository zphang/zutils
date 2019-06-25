import argparse
import os
import subprocess

from pyutils.io import read_json

ZSYNC_CONF_NAME = ".zsync.json"


def load_config(location):
    if not os.path.exists(ZSYNC_CONF_NAME):
        raise FileNotFoundError(ZSYNC_CONF_NAME)
    all_config = read_json(ZSYNC_CONF_NAME)
    if not all_config:
        raise RuntimeError("Config file is empty: {}".format(os.path.abspath(ZSYNC_CONF_NAME)))
    if location not in all_config:
        raise KeyError("'{}' config not found".format(location))
    return all_config[location]


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
    parser = argparse.ArgumentParser(description='PyTorch ImageNet Training')
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


if __name__ == "__main__":
    main()
