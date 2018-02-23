"""
$ python simple.py foo_value -b bar_value -h
usage: simple [-h] [-b BAR] foo

positional arguments:
  foo                positional argument

optional arguments:
  -h, --help         show this help message and exit
  -b BAR, --bar BAR  optional argument
                     with multiline help (default: default_for_bar)

examples:
    foo_value                                   positional arg only
    foo_value -b bar_value                      with optional arg
    foo_value --bar bar_value                   optional arg long-form
"""
from __future__ import print_function
import argutil

parser_def = argutil.ParserDefinition(__file__)
argparser = parser_def.get_parser()
opts = argparser.parse_args()
print('foo:', opts.foo)
print('bar:', opts.bar)
