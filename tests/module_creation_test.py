import unittest
from .helper import TempWorkingDirectory
import os
import sys
sys.path.insert(
    0,
    os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..'
    ))
)

import argutil  # noqa: E402

DEFINITIONS_FILE = argutil.defaults.DEFINITIONS_FILE


class ModuleCreationTest(unittest.TestCase):
    def test_add_example(self):
        with TempWorkingDirectory():
            module = 'test_script'
            argutil.init(module)
            argutil.add_example(
                module, 'usage text', 'description text'
            )
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
            self.assertDictEqual(argutil.load(DEFINITIONS_FILE), expected)

    def test_add_example_error_usage_not_str(self):
        with self.assertRaises(ValueError):
            argutil.add_example('test_script', 123)

    def test_add_example_error_description_not_str(self):
        with self.assertRaises(ValueError):
            argutil.add_example('test_script', 'usage text', ['description'])


if __name__ == '__main__':
    unittest.main()
