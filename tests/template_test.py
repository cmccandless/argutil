import unittest
from .helper import tempdir
from argutil import get_parser
from argutil.defaults import DEFINITIONS_FILE
import json


class TemplateTest(unittest.TestCase):
    @tempdir()
    def test_simple_template(self):
        json_data = {
            'modules': {
                'root': {
                    'args': [],
                    'templates': {'BASIC': {'args': [{'long': '--foo'}]}},
                    'modules': {'command': {'template': 'BASIC'}}
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        argparser = get_parser('root.py')
        opts = argparser.parse_args(['command', '--foo', 'bar'])
        self.assertEqual(opts.foo, 'bar')

    @tempdir()
    def test_template_inheritance(self):
        json_data = {
            'modules': {
                'root': {
                    'args': [],
                    'templates': {
                        'PARENT': {
                            'args': [{'long': '--foo'}]
                        },
                        'CHILD': {
                            'parent': 'PARENT',
                            'args': [{'long': '--bar'}]
                        }
                    },
                    'modules': {
                        'command': {
                            'args': [{'long': '--baz'}],
                            'template': 'CHILD'
                        }
                    }
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        argparser = get_parser('root.py')
        opts = argparser.parse_args([
            'command',
            '--foo', '1',
            '--bar', '2',
            '--baz', '3']
        )
        self.assertEqual(opts.foo, '1')
        self.assertEqual(opts.bar, '2')
        self.assertEqual(opts.baz, '3')

    @tempdir()
    def test_template_examples(self):
        json_data = {
            'modules': {
                'root': {
                    'args': [],
                    'templates': {
                        'BASIC': {
                            'examples': [
                                {
                                    'usage': '--foo',
                                    'description': 'usage from template'
                                }
                            ]
                        },
                        'COMPLEX': {
                            'parent': 'BASIC',
                            'examples': [
                                {
                                    'usage': '--bar',
                                    'description': 'usage from nested template'
                                }
                            ]
                        }
                    },
                    'modules': {
                        'command': {
                            'template': 'COMPLEX',
                            'examples': [
                                {
                                    'usage': '--baz',
                                    'description': 'usage from submodule'
                                }
                            ]
                        }
                    }
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        argparser = get_parser('root.py')
        expected = ['examples:']
        for u, d in [
            ('--foo', 'usage from template'),
            ('--bar', 'usage from nested template'),
            ('--baz', 'usage from submodule'),
        ]:
            expected.append('    {:<44}{}'.format(u, d))
        self.assertEqual(
            argparser._subparsers._group_actions[0].choices['command'].epilog,
            '\n'.join(expected)
        )

    @tempdir()
    def test_error_unknown_template(self):
        json_data = {
            'modules': {
                'root': {
                    'args': [],
                    'modules': {'command': {'template': 'BASIC'}}
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        with self.assertRaises(KeyError):
            get_parser('root.py')

    @tempdir()
    def test_error_unknown_parent_template(self):
        json_data = {
            'modules': {
                'root': {
                    'args': [],
                    'templates': {'MISSING_PARENT': {'parent': 'UNDEFINED'}},
                    'modules': {'command': {'template': 'MISSING_PARENT'}}
                }
            }
        }
        with open(DEFINITIONS_FILE, 'w') as f:
            f.write(json.dumps(json_data))
        with self.assertRaises(KeyError):
            get_parser('root.py')


if __name__ == '__main__':
    unittest.main()
