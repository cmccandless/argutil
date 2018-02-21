import tempfile
import shutil
from contextlib import contextmanager
import os
import sys
sys.path.insert(
    0,
    os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..'
    ))
)

import argutil


@contextmanager
def TempWorkingDirectory():
    wd = tempfile.mkdtemp()
    with argutil.WorkingDirectory(wd):
        yield wd
    shutil.rmtree(wd)


def tempdir(function):
    def wrapper(*args, **kwargs):
        with TempWorkingDirectory():
            function(*args, **kwargs)
    return wrapper
