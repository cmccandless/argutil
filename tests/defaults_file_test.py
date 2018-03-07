import unittest
from .helper import tempdir
import os
import argutil
from argutil import ParserDefinition

DEFAULTS_FILE = argutil.defaults.DEFAULTS_FILE


class DefaultsFileTest(unittest.TestCase):
    def assertCollectionEqual(self, col1, col2, msg=None):
        self.assertSequenceEqual(sorted(col1), sorted(col2), msg)

    @tempdir()
    def test_set_defaults_creates_file_if_nonexistent(self):
        self.assertIs(os.path.isfile(DEFAULTS_FILE), False)
        ParserDefinition.create('test_script.py').set_defaults()
        self.assertIs(os.path.isfile(DEFAULTS_FILE), True)

    @tempdir()
    def test_set_defaults_nested(self):
        parser_def = argutil.ParserDefinition.create('test_script.py')
        parser_def.set_defaults(**{"command1.command2": "value"})
        expected = {
            "test_script": {
                "command1": {
                    "command2": "value"
                }
            }
        }
        actual = argutil.load(parser_def.defaults_file)
        self.assertDictEqual(actual, expected)

    @tempdir()
    def test_get_defaults_nonexistent_defaults_file(self):
        parser_def = ParserDefinition.create('test_script.py')
        self.assertDictEqual(parser_def.get_defaults(), {})

    @tempdir()
    def test_get_defaults(self):
        expected = {}
        parser_def = ParserDefinition.create('test_script.py')
        parser_def.set_defaults()
        self.assertDictEqual(
            parser_def.get_defaults(),
            expected
        )

    @tempdir()
    def test_get_defaults_existing_entries(self):
        expected = {
            'foo': 'bar',
            'bar2': 'foo2'
        }
        parser_def = ParserDefinition.create('test_script.py')
        parser_def.set_defaults(foo='bar', bar2='foo2')
        self.assertDictEqual(
            parser_def.get_defaults(),
            expected
        )

    @tempdir()
    def test_get_defaults_nonexistent_module(self):
        expected = {}
        parser_def = ParserDefinition.create('test_script.py')
        parser_def.set_defaults(foo='bar')
        parser_def2 = ParserDefinition.create('other_script.py')
        self.assertDictEqual(parser_def2.get_defaults(), expected)

    @tempdir()
    def test_config_fetch_no_defaults(self):
        parser_def = ParserDefinition.create('test_script.py')
        current = parser_def.config()
        expected = []
        self.assertEqual(current, expected)

    @tempdir()
    def test_config_fetch_has_defaults(self):
        parser_def = ParserDefinition.create('test_script.py')
        parser_def.set_defaults(
            foo='bar',
            bar='foo'
        )
        current = parser_def.config()
        expected = [
            'foo=bar',
            'bar=foo'
        ]
        self.assertCollectionEqual(current, expected)

    @tempdir()
    def test_config_has_nested_defaults(self):
        parser_def = ParserDefinition.create('test_script.py')
        parser_def.set_defaults(**{
            "foo.bar.fee": "bar"
        })
        current = parser_def.config()
        expected = [
            'foo.bar.fee=bar'
        ]
        self.assertCollectionEqual(current, expected)

    @tempdir()
    def test_config_single_property(self):
        parser_def = ParserDefinition.create('test_script.py')
        parser_def.config(['foo=bar'])
        expected = {'foo': 'bar'}
        self.assertDictEqual(
            parser_def.get_defaults(),
            expected
        )

    @tempdir()
    def test_config_multiple_properties(self):
        parser_def = ParserDefinition.create('test_script.py')
        parser_def.config(
            [
                "a=1",
                "b='2'",
                'c="3"',
                "d=true",
                'e=9.2',
                "f='false'",
                "g=False",
                "h=None",
                "i=null"
            ]
        )
        expected = dict(
            a=1,
            b='2',
            c='3',
            d=True,
            e=9.2,
            f='false',
            g=False,
            h=None,
            i=None
        )
        self.assertDictEqual(
            parser_def.get_defaults(),
            expected
        )

    @tempdir()
    def test_config_list_property(self):
        parser_def = ParserDefinition.create('test_script.py')
        parser_def.config(
            ['foo=[1, "2", \'3\', true, false, none, null]']
        )
        expected = {'foo': [1, '2', '3', True, False, None, None]}
        self.assertDictEqual(
            parser_def.get_defaults(),
            expected
        )


if __name__ == '__main__':
    unittest.main()
