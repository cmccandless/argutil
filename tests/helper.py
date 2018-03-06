import tempfile
import shutil
from contextlib import contextmanager
import os
from sys import stdout
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


@contextmanager
def record_stdout(buf):
    old_write = stdout.write

    def new_write(s):
        buf.append(s)
        return len(s)

    setattr(stdout, 'write', new_write)
    yield
    setattr(stdout, 'write', old_write)
