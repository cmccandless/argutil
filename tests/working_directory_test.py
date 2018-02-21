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

from argutil import WorkingDirectory  # noqa: E402


class WorkingDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.wd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.wd)

    def test_cwd_is_changed(self):
        with open(os.path.join(self.wd, 'test.txt'), 'w') as f:
            f.write('it works!')
        with WorkingDirectory(self.wd):
            with open('test.txt') as f:
                self.assertEqual(f.read(), 'it works!')

    def test_cwd_set_to_parent_of_file(self):
        filepath = os.path.join(self.wd, 'test.txt')
        with open(filepath, 'w') as f:
            f.write('filepaths work!')
        with WorkingDirectory(filepath):
            with open('test.txt') as f:
                self.assertEqual(f.read(), 'filepaths work!')


if __name__ == '__main__':
    unittest.main()
