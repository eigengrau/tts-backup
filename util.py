from functools import partial


class ShadowProxy:
    """Proxy objects for arbitrary objects, with the ability to divert
    attribute access from one attribute to another.

    """

    def __init__(self, proxy_for):
        self.__target = proxy_for
        self.__diverted = {}

    def divert_access(self, source, target):
        self.__diverted[source] = target

    def __getattr__(self, name):
        if name in self.__diverted:
            name = self.__diverted[name]
        return getattr(self.__target, name)


def print_err(*args, **kwargs):
    # stderr could be reset at run-time, so we need to import it when
    # the function runs, not when this module is imported.
    from sys import stderr
    if 'file' in kwargs:
        del kwargs['file']
    print(*args, file=stderr, **kwargs)
