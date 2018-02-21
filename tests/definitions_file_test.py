import unittest
from .helper import TempWorkingDirectory
import json
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


class DefintionsFileTest(unittest.TestCase):
    def create_json_file(self, filename, json_data):
        with open(filename, 'w') as f:
            f.write(json.dumps(json_data))

    def test_load_returns_file_contents(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            expected = {
                'modules': {
                    'test_script': {}
                }
            }
            self.create_json_file(filename, expected)
            self.assertDictEqual(argutil.load(filename), expected)

    def test_load_returns_empty_data_on_nonexistent_file(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            self.assertIs(os.path.isfile(filename), False)
            expected = {'modules': {}}
            self.assertDictEqual(argutil.load(filename), expected)

    def test_load_nonexistent_file_not_created(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            self.assertIs(os.path.isfile(filename), False)
            argutil.load(filename)
            self.assertIs(os.path.isfile(filename), False)

    def test_load_error_nonexistent_file_mode_read_only(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            self.assertIs(os.path.isfile(filename), False)
            with self.assertRaises(FileNotFoundError):
                argutil.load(filename, 'r')

    def test_load_create_mode_ignores_file_contents(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            self.create_json_file(filename, {})
            expected = {
                'modules': {}
            }
            self.assertDictEqual(argutil.load(filename, 'w'), expected)

    def test_save_creates_nonexistent_file(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            self.assertIs(os.path.isfile(filename), False)
            argutil.save({}, filename)
            self.assertIs(os.path.isfile(filename), True)

    def test_save_overwrites_existing_file(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            self.create_json_file(filename, {})
            expected = {'modules': {}}
            argutil.save(expected, filename)
            with open(filename) as f:
                json_data = json.load(f)
            self.assertDictEqual(json_data, expected)

    def test_init_creates_script(self):
        with TempWorkingDirectory():
            argutil.init('test_script')
            self.assertIs(os.path.isfile('test_script.py'), True)

    def test_init_creates_definitions_file(self):
        with TempWorkingDirectory():
            argutil.init('test_script')
            self.assertIs(os.path.isfile('commandline.json'), True)

    def test_init_appends_to_existing_definitions_file(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            base_data = {
                'modules': {
                    'existing_module': {
                        'examples': [],
                        'args': []
                    }
                }
            }
            self.create_json_file(filename, base_data)
            argutil.init('test_script', filename)
            expected = {
                'modules': {
                    'existing_module': {
                        'examples': [],
                        'args': []
                    },
                    'test_script': {
                        'examples': [],
                        'args': []
                    }
                }
            }
            self.assertDictEqual(argutil.load(filename), expected)

    def test_init_definitions_file_contains_correct_structure(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            argutil.init('test_script', filename)
            expected = {
                'modules': {
                    'test_script': {
                        'examples': [],
                        'args': []
                    }
                }
            }
            self.assertDictEqual(argutil.load(filename), expected)

    def test_init_error_on_bad_definitions_file(self):
        with TempWorkingDirectory():
            filename = 'commandline.json'
            self.create_json_file(filename, {})
            with self.assertRaises(KeyError):
                argutil.init('test_script', filename)


if __name__ == '__main__':
    unittest.main()
