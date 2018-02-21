import os
from contextlib import contextmanager


@contextmanager
def WorkingDirectory(dir):
    if os.path.isfile(dir):
        dir = os.path.dirname(os.path.abspath(dir))
    cwd = os.getcwd()
    os.chdir(dir)
    yield
    os.chdir(cwd)
