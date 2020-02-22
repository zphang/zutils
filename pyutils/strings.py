def remove_prefix(s, prefix):
    assert s.startswith(prefix)
    return s[len(prefix):]
