"""
$ python submodules.py -h
usage: submodules [-h] [-c CONFIG] {this,that} ...

positional arguments:
  {this,that}

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        global option (default: None)

examples:
    this                                        subcommand
    -c config.cfg that                          subcommand with global option


$ python submodules.py this -h
usage: this [-h] [--then THEN] [--foo]

optional arguments:
  -h, --help   show this help message and exit
  --then THEN  option for this (default: None)
  --foo        this-exclusive flag (default: False)

examples:
    --then that                                 this then that


$ python submodules.py that -h
usage: that [-h] [--then THEN]

optional arguments:
  -h, --help   show this help message and exit
  --then THEN  option for that (default: None)

examples:
    --then this                                 that then this
"""
from __future__ import print_function
import argutil


@argutil.callable()
def this(opts):
    if opts.config:
        print('config:', opts.config)
    print('this was called')
    if opts.then:
        print('then:', opts.then)
    if opts.foo:
        print('foo set')


@argutil.callable()
def that(opts):
    if opts.config:
        print('config:', opts.config)
    print('that was called')
    if opts.then:
        print('then:', opts.then)


parser = argutil.get_parser()
opts = parser.parse_args()
opts.func(opts)
