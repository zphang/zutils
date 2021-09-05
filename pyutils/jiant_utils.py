import pyutils.io as io


def read_score(path):
    raw_scores = io.read_json(path)
    for task_name in ["quoref", "squad_v1"]:
        if task_name in raw_scores:
            return raw_scores["aggregated"] / 100
    return raw_scores["aggregated"]


def load_paths_scores(matches, metadata=None):
    for match in matches:
        match["score"] = read_score(match["path"])
        if metadata:
            for k, v in metadata.items():
                match[k] = v.format(**match)
    return matches
