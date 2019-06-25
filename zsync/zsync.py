import argparse
import os
import subprocess

from pyutils.io import read_json

ZSYNC_CONF_NAME = ".zsync.conf"


def load_config():
    return read_json(ZSYNC_CONF_NAME)


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
    tokens.append(src, dst)
    return tokens


def perform_command(tokens, show):
    if show:
        print(" \\\n    ".join(tokens))
    else:
        raise RuntimeError()
        result = subprocess.run(tokens, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout.decode('utf-8'))


def zsync_to(location, show):
    location_config = read_json(ZSYNC_CONF_NAME)[location]
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
    location_config = read_json(ZSYNC_CONF_NAME)[location]
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
    parser.add_argument('--show')
    args = parser.parse_args()


if __name__ == "__main__":
    main()
