import unittest
from argutil.deepcopy import deepcopy


class DeepCopyTest(unittest.TestCase):
    def test_deepcopy_list(self):
        src = [1, 2, 3, 4]
        dst = deepcopy(src)
        self.assertSequenceEqual(src, dst)

    def test_deepcopy_list_modify_source(self):
        src = [1, 2, 3, 4]
        dst = deepcopy(src)
        src.append(5)
        self.assertSequenceEqual(src, dst + [5])

    def test_deepcopy_list_modify_destination(self):
        src = [1, 2, 3, 4]
        dst = deepcopy(src)
        dst.append(5)
        self.assertSequenceEqual(src + [5], dst)

    def test_deepcopy_set(self):
        src = {1, 2, 3, 4}
        dst = deepcopy(src)
        self.assertSequenceEqual(src, dst)

    def test_deepcopy_set_modify_source(self):
        src = {1, 2, 3, 4}
        dst = deepcopy(src)
        src.add(5)
        self.assertSequenceEqual(src, dst.union([5]))

    def test_deepcopy_set_modify_destination(self):
        src = {1, 2, 3, 4}
        dst = deepcopy(src)
        dst.add(5)
        self.assertSequenceEqual(src.union([5]), dst)

    def test_deepcopy_dict(self):
        src = dict(a=1, b=2, c=3)
        dst = deepcopy(src)
        self.assertSequenceEqual(src, dst)

    def test_deepcopy_dict_modify_source(self):
        src = dict(a=1, b=2, c=3)
        dst = deepcopy(src)
        src['d'] = 4
        self.assertNotIn('d', dst)

    def test_deepcopy_dict_modify_destination(self):
        src = dict(a=1, b=2, c=3)
        dst = deepcopy(src)
        dst['d'] = 4
        self.assertNotIn('d', src)

    def test_deepcopy_nested(self):
        src = {
            'list': [1, 2, 3, 4],
            'set': {'a', 'b', 'c'}
        }
        dst = deepcopy(src)
        self.assertDictEqual(src, dst)

    def test_deepcopy_nested_modify_source(self):
        src = {
            'list': [1, 2, 3, 4],
            'set': {'a', 'b', 'c'}
        }
        dst = deepcopy(src)
        src['list'].append(5)
        self.assertNotEqual(src, dst)
        self.assertSequenceEqual(src['list'], dst['list'] + [5])

    def test_deepcopy_nested_modify_destination(self):
        src = {
            'list': [1, 2, 3, 4],
            'set': {'a', 'b', 'c'}
        }
        dst = deepcopy(src)
        dst['set'].add('d')
        self.assertNotEqual(src, dst)
        self.assertSequenceEqual(src['set'].union('d'), dst['set'])


if __name__ == '__main__':
    unittest.main()
