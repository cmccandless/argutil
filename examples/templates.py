"""
$ python templates.py -h
usage: templates [-h] {command} ...

positional arguments:
  {command}

optional arguments:
  -h, --help  show this help message and exit

$ python templates.py command -h
usage: command [-h] [--baz BAZ] [--foo FOO] [--bar BAR]

optional arguments:
  -h, --help  show this help message and exit
  --baz BAZ
  --foo FOO
  --bar BAR

examples:
    --foo                                       example from parent template
    --bar                                       example from child template
    --baz                                       example from command
"""
from __future__ import print_function
import argutil


@argutil.callable()
def command(opts):
    print(opts.__dict__)


parser = argutil.get_parser()
opts = parser.parse_args()
opts.func(opts)
