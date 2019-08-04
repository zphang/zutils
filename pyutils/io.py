import json


def read_file(path, mode="r", **kwargs):
    with open(path, mode=mode, **kwargs) as f:
        return f.read()


def write_file(data, path, mode="w", **kwargs):
    with open(path, mode=mode, **kwargs) as f:
        f.write(data)


def read_json(path):
    return json.loads(read_file(path))


def write_json(data, path):
    return write_file(json.dumps(data, indent=2), path)


def read_jsonl(path):
    # Manually open because .splitlines is different from iterating over lines
    ls = []
    with open(path, "r") as f:
        for line in f:
            ls.append(json.loads(line))
    return ls


def write_jsonl(data, path):
    lines = [
        json.dumps(elem).replace("\n", "")
        for elem in data
    ]
    write_file("\n".join(lines), path)


def read_file_lines(path, mode="r", encoding="utf-8", **kwargs):
    with open(path, mode=mode, encoding=encoding, **kwargs) as f:
        return f.readlines()
