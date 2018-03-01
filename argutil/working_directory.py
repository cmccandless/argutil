import os
from contextlib import contextmanager


@contextmanager
def WorkingDirectory(dir):
    if not os.path.isdir(dir):
        dir = os.path.dirname(os.path.abspath(dir))
    cwd = os.getcwd()
    if cwd != dir:
        os.chdir(dir)
        yield
        os.chdir(cwd)
    else:
        yield


def pushd(path):
    def _dec(function):
        def _wrapper(*args, **kwargs):
            with WorkingDirectory(path):
                function(*args, **kwargs)
        return _wrapper
    return _dec
