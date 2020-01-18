import glob
import re


def tags_to_regex(tag_pattern, format_dict=None, default_format="\\w+"):
    if format_dict is None:
        format_dict = {}
    last_end = 0
    new_tokens = []
    for m in re.finditer("\\{(?P<tag>\\w+)\\}", tag_pattern):
        start, end = m.span()
        tag = m["tag"]
        new_tokens.append(tag_pattern[last_end:start])
        tag_format = format_dict.get(tag, default_format)
        new_tokens.append(f"(?P<{tag}>{tag_format})")
        last_end = end
    new_tokens.append(tag_pattern[last_end:])
    new_pattern = "".join(new_tokens)
    return new_pattern


def match_paths(path_pattern):
    path_ls = sorted(glob.glob(re.sub(r"{(\w+)}", "*", path_pattern)))
    regex = re.compile(tags_to_regex(path_pattern))
    result_ls = []
    for path in path_ls:
        result = next(regex.finditer(path)).groupdict()
        assert "path" not in result, "keyword clash: \"path\""
        result["path"] = path
        result_ls.append(result)
    return result_ls
