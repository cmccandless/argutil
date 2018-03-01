import unittest
from .helper import tempdir
import json
import os
import argutil


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

DEFINITIONS_FILE = argutil.defaults.DEFINITIONS_FILE


class DefinitionsFileTest(unittest.TestCase):
    def create_json_file(self, filename, json_data):
        with open(filename, 'w') as f:
            f.write(json.dumps(json_data))

    @tempdir()
    def test_load_returns_file_contents(self):
        expected = {
            'modules': {
                'test_script': {}
            }
        }
        self.create_json_file(DEFINITIONS_FILE, expected)
        self.assertDictEqual(argutil.load(DEFINITIONS_FILE), expected)

    @tempdir()
    def test_load_returns_empty_data_on_nonexistent_file(self):
        self.assertIs(os.path.isfile(DEFINITIONS_FILE), False)
        expected = {}
        self.assertDictEqual(argutil.load(DEFINITIONS_FILE), expected)

    @tempdir()
    def test_load_nonexistent_file_not_created(self):
        self.assertIs(os.path.isfile(DEFINITIONS_FILE), False)
        argutil.load(DEFINITIONS_FILE)
        self.assertIs(os.path.isfile(DEFINITIONS_FILE), False)

    @tempdir()
    def test_load_error_nonexistent_file_mode_read_only(self):
        self.assertIs(os.path.isfile(DEFINITIONS_FILE), False)
        with self.assertRaises(FileNotFoundError):
            argutil.load(DEFINITIONS_FILE, 'r')

    @tempdir()
    def test_load_create_mode_ignores_file_contents(self):
        self.create_json_file(DEFINITIONS_FILE, {})
        expected = {}
        self.assertDictEqual(argutil.load(DEFINITIONS_FILE, 'w'), expected)

    def test_load_error_unknown_file_mode(self):
        with self.assertRaises(ValueError):
            argutil.load(DEFINITIONS_FILE, 'u')

    @tempdir()
    def test_save_creates_nonexistent_file(self):
        filename = 'commandline.json'
        self.assertIs(os.path.isfile(DEFINITIONS_FILE), False)
        argutil.save({}, filename)
        self.assertIs(os.path.isfile(DEFINITIONS_FILE), True)

    @tempdir()
    def test_save_overwrites_existing_file(self):
        self.create_json_file(DEFINITIONS_FILE, {})
        expected = {'modules': {}}
        argutil.save(expected, DEFINITIONS_FILE)
        with open(DEFINITIONS_FILE) as f:
            json_data = json.load(f)
        self.assertDictEqual(json_data, expected)


class ParserDefinitionTest(unittest.TestCase):
    def create_json_file(self, filename, json_data):
        with open(filename, 'w') as f:
            f.write(json.dumps(json_data))

    @tempdir()
    def test_create_creates_script(self):
        argutil.ParserDefinition.create('test_script.py')
        self.assertIs(os.path.isfile('test_script.py'), True)

    @tempdir()
    def test_create_creates_definitions_file(self):
        argutil.ParserDefinition.create('test_script.py')
        self.assertIs(os.path.isfile('commandline.json'), True)

    @tempdir()
    def test_create_error_existing_module(self):
        filename = 'test_script.py'
        argutil.ParserDefinition.create(filename)
        with self.assertRaises(KeyError):
            argutil.ParserDefinition.create(filename)

    @tempdir()
    def test_init_nonexistent_module(self):
        with self.assertRaises(SystemExit):
            argutil.ParserDefinition('test_script.py').get_parser()

    @tempdir()
    def test_create_appends_to_existing_definitions_file(self):
        base_data = {
            'modules': {
                'existing_module': {
                    'examples': [],
                    'args': []
                }
            }
        }
        self.create_json_file(DEFINITIONS_FILE, base_data)
        argutil.ParserDefinition.create('test_script.py', DEFINITIONS_FILE)
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
        self.assertDictEqual(argutil.load(DEFINITIONS_FILE), expected)

    @tempdir()
    def test_init_definitions_file_contains_correct_structure(self):
        argutil.ParserDefinition.create('test_script.py', DEFINITIONS_FILE)
        expected = {
            'modules': {
                'test_script': {
                    'examples': [],
                    'args': []
                }
            }
        }
        self.assertDictEqual(argutil.load(DEFINITIONS_FILE), expected)

    @tempdir()
    def test_init_error_on_bad_definitions_file(self):
        self.create_json_file(DEFINITIONS_FILE, {})
        with self.assertRaises(KeyError):
            argutil.ParserDefinition.create('test_script.py', DEFINITIONS_FILE)


if __name__ == '__main__':
    unittest.main()
