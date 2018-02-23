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

WD = os.path.abspath(os.path.join('.', 'tmp'))


@contextmanager
def TempWorkingDirectory(dir=None, cleanup=True):
    wd = tempfile.mkdtemp(dir=dir)
    with argutil.WorkingDirectory(wd):
        yield wd
    if cleanup:
        shutil.rmtree(wd)


def tempdir(dir=None, cleanup=True):
    def dec(function):
        def wrapper(*args, **kwargs):
            with TempWorkingDirectory(dir, cleanup):
                function(*args, **kwargs)
        return wrapper
    return dec
