from functools import wraps


def lazy_str(func):
    """
    Wraps `func` so that it is called when caller wants __str__().
    :param func: callable to defer.
    """

    @wraps(func)
    class LazyStr:
        def __str__(self):
            return func()

    return LazyStr()
