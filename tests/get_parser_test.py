import unittest
from .helper import WD, tempdir
import argutil
from argutil import ParserDefinition
from jsonschema import ValidationError

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
            parser_def = ParserDefinition.create(cls.filepath)

            def add_arg(name, **kwargs):
                return parser_def.add_argument(name, **kwargs)
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
            parser_def.env['hex'] = lambda s: hex(int(s))
            add_arg('--def-env-type', type='hex')
            argutil.GLOBAL_ENV['u_str'] = lambda s: s.upper()
            add_arg('--global-env-type', type='u_str')
            add_arg('--default-from-file')
            parser_def.add_example(
                'test --flag', 'positional w/ optional flag'
            )
            parser_def.set_defaults(default_from_file=123)
            cls.parser = parser_def.get_parser(env=cls.env)

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

    def test_parser_definition_type_option(self):
        self.assertIs(
            self.get_opts('test').def_env_type,
            None
        )
        self.assertEqual(
            self.get_opts(
                'test', '--def-env-type', '255'
            ).def_env_type,
            '0xff'
        )

    def test_global_env_type_option(self):
        self.assertIs(
            self.get_opts('test').global_env_type,
            None
        )
        self.assertEqual(
            self.get_opts(
                'test', '--global-env-type', 'abc'
            ).global_env_type,
            'ABC'
        )

    def test_default_from_file(self):
        self.assertEqual(self.get_opts('test').default_from_file, 123)

    @tempdir(WD)
    def test_module_not_in_defaults_file(self):
        this_def = argutil.ParserDefinition.create('this_script')
        this_def.add_argument('--foo')
        this_def.set_defaults(foo='bar')
        that_def = argutil.ParserDefinition.create('that_script')
        that_def.add_argument('--foo')
        that_parser = that_def.get_parser()
        that_opts = that_parser.parse_args([])
        self.assertIs(that_opts.foo, None)

    @tempdir(WD)
    def test_error_bad_definitions_file(self):
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write('{"bad_def":{}}')
        with self.assertRaises(ValidationError):
            argutil.get_parser('bad_def.py')

    @tempdir(WD)
    def test_error_non_existent_module(self):
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write('{"modules":{}}')
        with self.assertRaises(KeyError):
            argutil.get_parser('bad_def.py')

    @tempdir(WD)
    def test_error_unknown_type(self):
        filename = 'bad_module.py'
        parser_def = ParserDefinition.create(filename)
        parser_def.add_argument('unknown_type', type='shoe')
        with self.assertRaises(KeyError):
            parser_def.get_parser()

    @tempdir(WD)
    def test_error_missing_long_key(self):
        filename = 'bad_module.py'
        parser_def = ParserDefinition.create(filename)
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
        with self.assertRaises(ValidationError):
            parser_def.get_parser()


if __name__ == '__main__':
    unittest.main()
