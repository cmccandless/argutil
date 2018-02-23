import unittest
from .helper import WD, tempdir
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

DEFINITIONS_FILE = argutil.defaults.DEFINITIONS_FILE
DEFAULTS_FILE = argutil.defaults.DEFAULTS_FILE

try:
    PermissionError
except NameError:
    class PermissionError(Exception):
        pass

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class GetParserTest(unittest.TestCase):
    def assertCollectionEqual(self, col1, col2, msg=None):
        self.assertSequenceEqual(sorted(col1), sorted(col2), msg)

    @classmethod
    def setUpClass(cls):
        cls.filepath = 'test_script.py'
        cls.module = argutil.get_module(cls.filepath)
        cls.env = {
            'l_str': lambda s: str(s).lower(),
        }
        with argutil.WorkingDirectory(WD):
            def add_arg(name, **kwargs):
                return argutil.add_argument(cls.module, name, **kwargs)
            argutil.init(cls.module)
            add_arg('positional')
            add_arg('positional_list', nargs='*', type=int)
            add_arg('--flag', action='store_true', help='boolean flag option')
            add_arg('--opt', short='-o', type='int')
            add_arg('--opt-list', nargs='+', type=str)
            add_arg(
                '--opt-list-with-default',
                nargs='+',
                default=[]
            )
            add_arg('--env-type', type='l_str')
            argutil.add_example(
                cls.module,
                'test --flag', 'positional w/ optional flag'
            )
            cls.parser = argutil.get_parser(cls.filepath, env=cls.env)

    def get_opts(self, *args):
        with argutil.WorkingDirectory(WD):
            return GetParserTest.parser.parse_args(args)

    def test_positional(self):
        self.assertEqual(self.get_opts('test').positional, 'test')

    def test_positional_list(self):
        opts = self.get_opts('test', '1', '2', '3')
        self.assertEqual(opts.positional, 'test')
        self.assertCollectionEqual(opts.positional_list, [1, 2, 3])

    def test_positional_required(self):
        with self.assertRaises(SystemExit):
            self.get_opts()

    def test_positional_required_with_optional(self):
        with self.assertRaises(SystemExit):
            self.get_opts('--flag')

    def test_flag(self):
        self.assertIs(self.get_opts('test').flag, False)
        self.assertIs(self.get_opts('test', '--flag').flag, True)

    def test_list_option(self):
        self.assertIs(self.get_opts('test').opt_list, None)
        self.assertListEqual(
            self.get_opts(
                'test', '--opt-list', '1', 'b', '3'
            ).opt_list,
            ['1', 'b', '3']
        )

    def test_list_option_with_default(self):
        self.assertListEqual(
            self.get_opts('test').opt_list_with_default,
            []
        )
        self.assertListEqual(
            self.get_opts(
                'test', '--opt-list-with-default', '1', 'b', '3'
            ).opt_list_with_default,
            ['1', 'b', '3']
        )

    def test_env_type_option(self):
        self.assertIs(
            self.get_opts('test').env_type,
            None
        )
        self.assertEqual(
            self.get_opts(
                'test', '--env-type', 'ABC'
            ).env_type,
            'abc'
        )

    @tempdir(WD)
    def test_error_unknown_type(self):
        filename = 'bad_module.py'
        module = argutil.get_module(filename)
        argutil.init(module)
        argutil.add_argument(module, 'unknown_type', type='shoe')
        with self.assertRaises(KeyError):
            argutil.get_parser(filename, env={})

    @tempdir(WD)
    def test_error_missing_long_key(self):
        filename = 'bad_module.py'
        module = argutil.get_module(filename)
        argutil.init(module)
        json_data = {
            'modules': {
                'bad_module': {
                    'examples': [],
                    'args': [
                        {
                            'help': ['no help for you']
                        }
                    ]
                }
            }
        }
        argutil.save(json_data, DEFINITIONS_FILE)
        with self.assertRaises(ValueError):
            argutil.get_parser('bad_module.py')


if __name__ == '__main__':
    unittest.main()
