import unittest
from .helper import tempdir, record_stdout
from argutil import callable, get_parser, ParserDefinition
from argutil.defaults import DEFINITIONS_FILE
import json
import sys


class SubmoduleTest(unittest.TestCase):
    @tempdir()
    def test_simple_submodule(self):
        json_data = {
            'modules': {
                'root': {'modules': {'command': {'args': [{'long': '--foo'}]}}}
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        argparser = get_parser('root.py')
        opts = argparser.parse_args(['command', '--foo', 'bar'])
        self.assertEqual(opts.foo, 'bar')

    @tempdir()
    def test_submodule_aliases(self):
        if sys.version_info[0] < 3:
            self.skipTest('feature not available in Python2')
        json_data = {
            'modules': {
                'root': {
                    'modules': {
                        'command': {
                            'aliases': ['c'],
                            'args': [{'long': '--foo'}]
                        }
                    }
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        argparser = get_parser('root.py')
        opts = argparser.parse_args(['c', '--foo', 'bar'])
        self.assertEqual(opts.foo, 'bar')

    @tempdir()
    def test_submodule_default_handler_shows_usage(self):
        json_data = {
            'modules': {
                'root': {'modules': {'command': {'args': [{'long': '--foo'}]}}}
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        argparser = get_parser('root.py')
        opts = argparser.parse_args(['command'])
        buf = []
        with record_stdout(buf):
            opts.func(opts)
        actual = ''.join(buf)
        expected = '\n'.join([
            'usage: command [-h] [--foo FOO]',
            '',
            'optional arguments:',
            '  -h, --help  show this help message and exit',
            '  --foo FOO\n',
        ])
        self.assertEqual(actual, expected)

    @tempdir()
    def test_submodule_handler_env(self):
        json_data = {
            'modules': {
                'root': {
                    'modules': {
                        'command': {
                            'args': [{'long': '--foo'}]
                        }
                    }
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))

        def get_opts(opts):
            return 'get_opts called: foo={}'.format(opts.foo)
        argparser = get_parser('root.py', env={'command': get_opts})
        opts = argparser.parse_args(['command', '--foo', 'bar'])
        expected = 'get_opts called: foo=bar'
        self.assertEqual(opts.func(opts), expected)

    @tempdir()
    def test_submodule_handler_global_callable_decorator(self):
        json_data = {
            'modules': {
                'root': {
                    'modules': {
                        'command': {
                            'args': [{'long': '--foo'}]
                        }
                    }
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))

        @callable('command')
        def get_opts(opts):
            return 'get_opts called: foo={}'.format(opts.foo)
        argparser = get_parser('root.py')
        opts = argparser.parse_args(['command', '--foo', 'bar'])
        expected = 'get_opts called: foo=bar'
        self.assertEqual(opts.func(opts), expected)

    @tempdir()
    def test_submodule_handler_definition_callable_decorator(self):
        json_data = {
            'modules': {
                'root': {
                    'modules': {
                        'command': {
                            'args': [{'long': '--foo'}]
                        }
                    }
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        parser_def = ParserDefinition('root.py')

        @parser_def.callable('command')
        def get_opts(opts):
            return 'get_opts called: foo={}'.format(opts.foo)
        argparser = parser_def.get_parser()
        opts = argparser.parse_args(['command', '--foo', 'bar'])
        expected = 'get_opts called: foo=bar'
        self.assertEqual(opts.func(opts), expected)

    @tempdir()
    def test_nested_submodules(self):
        json_data = {
            'modules': {
                'root': {
                    'modules': {
                        'command': {
                            'args': [{'long': '--foo'}],
                            'modules': {
                                'subcommand': {
                                    'args': [{'long': '--bar'}]
                                }
                            }
                        }
                    }
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        argparser = get_parser('root.py')
        opts = argparser.parse_args([
            'command', '--foo', 'bar',
            'subcommand', '--bar', 'baz'
        ])
        self.assertEqual(opts.foo, 'bar')
        self.assertEqual(opts.bar, 'baz')

    @tempdir()
    def test_submodule_option_defaults(self):
        json_data = {
            'modules': {
                'root': {
                    'modules': {
                        'command': {
                            'args': [{'long': '--foo'}]
                        }
                    }
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        parser_def = ParserDefinition('root.py')
        parser = parser_def.get_parser()
        opts = parser.parse_args(['command'])
        self.assertIsNone(opts.foo)

        parser_def.set_defaults(**{'command.foo': 'bar'})
        parser = parser_def.get_parser()
        opts = parser.parse_args(['command'])
        self.assertEqual(opts.foo, 'bar')


if __name__ == '__main__':
    unittest.main()
