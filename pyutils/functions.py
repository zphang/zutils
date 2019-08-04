import inspect


def populate_args(func, reference):
    staged_kwargs = {}
    for arg_name in inspect.signature(func).parameters:
        if hasattr(reference, arg_name):
            staged_kwargs[arg_name] = getattr(reference, arg_name)

    def new_func(*args, **kwargs):
        final_kwargs = staged_kwargs.copy()
        for k, v in kwargs.items():
            final_kwargs[k] = v
        return func(*args, **final_kwargs)

    return new_func
