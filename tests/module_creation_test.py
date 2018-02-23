import unittest
from .helper import WD, TempWorkingDirectory
from contextlib import contextmanager
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


class ModuleCreationTest(unittest.TestCase):
    @contextmanager
    def assertModifiedModule(self, expected=None, module='test_script'):
        with TempWorkingDirectory(WD, False):
            argutil.init(module)
            yield module
            self.assertDictEqual(argutil.load(DEFINITIONS_FILE), expected)

    def test_add_example(self):
        expected = {
            'modules': {
                'test_script': {
                    'examples': [
                        {
                            'usage': 'usage text',
                            'description': 'description text'
                        }
                    ],
                    'args': []
                }
            }
        }
        with self.assertModifiedModule(expected) as module:
            argutil.add_example(module, 'usage text', 'description text')

    def test_add_example_error_usage_not_str(self):
        with self.assertRaises(ValueError):
            argutil.add_example('test_script', 123)

    def test_add_example_error_description_not_str(self):
        with self.assertRaises(ValueError):
            argutil.add_example('test_script', 'usage text', ['description'])

    def test_add_argument_positional(self):
        expected = {
            'modules': {
                'test_script': {
                    'examples': [],
                    'args': [
                        {
                            'long': 'foo',
                            'help': None
                        }
                    ]
                }
            }
        }
        with self.assertModifiedModule(expected) as module:
            argutil.add_argument(module, 'foo')

    def test_add_argument_help_is_none(self):
        expected = {
            'modules': {
                'test_script': {
                    'examples': [],
                    'args': [
                        {
                            'long': 'foo',
                            'help': None
                        }
                    ]
                }
            }
        }
        with self.assertModifiedModule(expected) as module:
            argutil.add_argument(module, 'foo', help=None)

    def test_add_argument_help_is_str(self):
        expected = {
            'modules': {
                'test_script': {
                    'examples': [],
                    'args': [
                        {
                            'long': 'foo',
                            'help': [
                                'foo help'
                            ]
                        }
                    ]
                }
            }
        }
        with self.assertModifiedModule(expected) as module:
            argutil.add_argument(module, 'foo', help='foo help')

    def test_add_argument_help_is_multiline_str(self):
        expected = {
            'modules': {
                'test_script': {
                    'examples': [],
                    'args': [
                        {
                            'long': 'foo',
                            'help': [
                                'foo',
                                'help'
                            ]
                        }
                    ]
                }
            }
        }
        with self.assertModifiedModule(expected) as module:
            argutil.add_argument(module, 'foo', help='foo\nhelp')

    def test_add_argument_help_is_list(self):
        expected = {
            'modules': {
                'test_script': {
                    'examples': [],
                    'args': [
                        {
                            'long': 'foo',
                            'help': [
                                'foo',
                                'help'
                            ]
                        }
                    ]
                }
            }
        }
        with self.assertModifiedModule(expected) as module:
            argutil.add_argument(module, 'foo', help=['foo', 'help'])

    def test_add_argument_error_help_is_bad_type(self):
        with self.assertRaises(TypeError):
            with self.assertModifiedModule() as module:
                argutil.add_argument(module, 'foo', help=True)

    def test_add_argument_error_help_is_list_of_non_strings(self):
        with self.assertRaises(TypeError):
            with self.assertModifiedModule() as module:
                argutil.add_argument(module, 'foo', help=[123, True])

    def test_add_argument_optional(self):
        expected = {
            'modules': {
                'test_script': {
                    'examples': [],
                    'args': [
                        {
                            'short': '-f',
                            'long': '--foo',
                            'help': None
                        }
                    ]
                }
            }
        }
        with self.assertModifiedModule(expected) as module:
            argutil.add_argument(module, '--foo', short='-f')

    def test_add_argument_flag(self):
        expected = {
            'modules': {
                'test_script': {
                    'examples': [],
                    'args': [
                        {
                            'long': '--foo',
                            'action': 'store_true',
                            'help': None
                        }
                    ]
                }
            }
        }
        with self.assertModifiedModule(expected) as module:
            argutil.add_argument(module, '--foo', action='store_true')

    def test_add_argument_list_arg(self):
        expected = {
            'modules': {
                'test_script': {
                    'examples': [],
                    'args': [
                        {
                            'long': 'foo',
                            'nargs': '+',
                            'help': None
                        }
                    ]
                }
            }
        }
        with self.assertModifiedModule(expected) as module:
            argutil.add_argument(module, 'foo', nargs='+')

    def test_add_argument_error_bad_key(self):
        with self.assertRaises(KeyError):
            with self.assertModifiedModule() as module:
                argutil.add_argument(module, 'foo', var='foo')


if __name__ == '__main__':
    unittest.main()
