import json
import tqdm


def maybe_tqdm(iterable=None, desc=None, total=None, verbose=True):
    if verbose:
        return tqdm.tqdm(
            iterable=iterable,
            desc=desc,
            total=total,
        )
    else:
        return iterable


def maybe_trange(*args, verbose, **kwargs):
    return maybe_tqdm(range(*args), verbose=verbose, **kwargs)


def show_json(obj, do_print=True):
    string = json.dumps(obj, indent=2)
    if do_print:
        print(string)
    else:
        return string
