import unittest
import tempfile
import shutil
import os
import sys
sys.path.insert(
    0,
    os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..'
    ))
)

from argutil import WorkingDirectory, pushd


class WorkingDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.wd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.wd)

    def test_cwd_is_changed(self):
        filename = 'dirpath.txt'
        with open(os.path.join(self.wd, filename), 'w') as f:
            f.write('it works!')
        with WorkingDirectory(self.wd):
            with open(filename) as f:
                self.assertEqual(f.read(), 'it works!')

    def test_cwd_set_to_parent_of_file(self):
        filename = 'filepath.txt'
        filepath = os.path.join(self.wd, filename)
        with open(filepath, 'w') as f:
            f.write('filepaths work!')
        with WorkingDirectory(filepath):
            with open(filename) as f:
                self.assertEqual(f.read(), 'filepaths work!')

    def test_pushd(self):
        filename = 'pushd.txt'
        with open(os.path.join(self.wd, filename), 'w') as f:
            f.write('pushd works!')

        @pushd(self.wd)
        def in_wd():
            with open(filename) as f:
                self.assertEqual(f.read(), 'pushd works!')
        self.assertIs(os.path.isfile(filename), False)
        in_wd()


if __name__ == '__main__':
    unittest.main()
