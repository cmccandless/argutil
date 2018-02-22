import unittest
from .helper import tempdir
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

DEFAULTS_FILE = argutil.defaults.DEFAULTS_FILE


class DefaultsFileTest(unittest.TestCase):
    def assertCollectionEqual(self, col1, col2, msg=None):
        self.assertSequenceEqual(sorted(col1), sorted(col2), msg)

    @tempdir()
    def test_set_defaults_creates_file_if_nonexistent(self):
        self.assertIs(os.path.isfile(DEFAULTS_FILE), False)
        argutil.set_defaults('test_script', DEFAULTS_FILE)
        self.assertIs(os.path.isfile(DEFAULTS_FILE), True)

    @tempdir()
    def test_get_defaults_nonexistent_defaults_file(self):
        self.assertDictEqual(argutil.get_defaults('test_script'), {})

    @tempdir()
    def test_get_defaults(self):
        expected = {}
        module = 'test_script'
        argutil.set_defaults(module, DEFAULTS_FILE)
        self.assertDictEqual(
            argutil.get_defaults(module, DEFAULTS_FILE),
            expected
        )

    @tempdir()
    def test_get_defaults_existing_entries(self):
        expected = {
            'foo': 'bar',
            'bar2': 'foo2'
        }
        module = 'test_script'
        argutil.set_defaults(module, DEFAULTS_FILE, foo='bar', bar2='foo2')
        self.assertDictEqual(
            argutil.get_defaults(module, DEFAULTS_FILE),
            expected
        )

    @tempdir()
    def test_get_defaults_nonexistent_module(self):
        expected = {}
        argutil.set_defaults('test_script', foo='bar')
        self.assertDictEqual(argutil.get_defaults('other_script'), expected)

    @tempdir()
    def test_config_fetch_no_defaults(self):
        module = 'test_script'
        current = list(argutil.config(module, []))
        expected = []
        self.assertEqual(current, expected)

    @tempdir()
    def test_config_fetch_has_defaults(self):
        module = 'test_script'
        argutil.set_defaults(
            module,
            defaults_file=DEFAULTS_FILE,
            foo='bar',
            bar='foo'
        )
        current = argutil.config(module)
        expected = [
            'foo=bar',
            'bar=foo'
        ]
        self.assertCollectionEqual(current, expected)

    @tempdir()
    def test_config_single_property(self):
        module = 'test_script'
        argutil.config(module, ['foo=bar'])
        expected = {'foo': 'bar'}
        self.assertDictEqual(
            argutil.get_defaults(module, DEFAULTS_FILE),
            expected
        )

    @tempdir()
    def test_config_multiple_properties(self):
        module = 'test_script'
        argutil.config(
            module,
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
            argutil.get_defaults(module, DEFAULTS_FILE),
            expected
        )

    @tempdir()
    def test_config_list_property(self):
        module = 'test_script'
        argutil.config(
            module,
            ['foo=[1, "2", \'3\', true, false, none, null]']
        )
        expected = {'foo': [1, '2', '3', True, False, None, None]}
        self.assertDictEqual(
            argutil.get_defaults(module, DEFAULTS_FILE),
            expected
        )


if __name__ == '__main__':
    unittest.main()
