#!/usr/bin/env python
import argutil
import os
import sys

__filename__ = '.'.join(__file__.split(os.path.sep)[-1].split('.')[:-1])
try:
    if __module__ is None:
        __module__ = __filename__
except NameError:
    __module__ = __filename__

with argutil.WorkingDirectory(__file__):
    parser = argutil.getParser(__module__)


def run(opts):
    return 0


if __name__ == '__main__':
    sys.exit(run(parser.parse_args()))
