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


def this(opts):
    if opts.config:
        print('config:', opts.config)
    print('this was called')
    if opts.then:
        print('then:', opts.then)
    if opts.foo:
        print('foo set')


def that(opts):
    if opts.config:
        print('config:', opts.config)
    print('that was called')
    if opts.then:
        print('then:', opts.then)


env = {
    'this': this,
    'that': that
}
parser_def = argutil.ParserDefinition(__file__)
parser = parser_def.get_parser(env)
opts = parser.parse_args()
opts.func(opts)
