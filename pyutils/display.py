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
