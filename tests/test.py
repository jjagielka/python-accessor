"""Test module."""

import unittest

from accessor import accessor as _, flatten


tester = [
    {
        'a': 1,
        'b': {'c': 5, 'cc': {'d': 6, 'e': 7}},
        'f': [
            {'g': 11, 'h': 12},
            {'g': 13, 'h': 14},
        ]
    },
    {
        'a': 3,
        'b': {'c': 8, 'cc': {'d': 9, 'e': 10}},
        'f': [
            {'g': 21, 'h': 22},
            {'g': 23, 'h': 24},
        ]
    }
]


class TestGetter(unittest.TestCase):

    def test_identity(self):
        self.assertEqual(_(tester[0]), tester[0])
        self.assertEqual(list(map(_, tester)), tester)

    def test_1st_level(self):
        self.assertEqual(_.a(tester[0]), 1)
        self.assertEqual(list(map(_.a, tester)), [1, 3])

    def test_2nd_level(self):
        self.assertEqual(_.b.c(tester[0]), 5)
        self.assertEqual(list(map(_.b.c, tester)), [5, 8])

    def test_3rd_level(self):
        self.assertEqual(_.b.cc.d(tester[0]), 6)
        self.assertEqual(list(map(_.b.cc.d, tester)), [6, 9])

    def test_filter_level(self):
        self.assertEqual(list(filter(_.b.cc.d > 7, tester)), tester[1:])

    def test_flatten(self):
        result = [
            [{'a': 1, 'c': 5, 'g_c': 11, 'h_c': 12},
             {'a': 1, 'c': 5, 'g_c': 13, 'h_c': 14}],
            [{'a': 3, 'c': 8, 'g_c': 21, 'h_c': 22},
             {'a': 3, 'c': 8, 'g_c': 23, 'h_c': 24}]]
        self.assertEqual(list(map(flatten(_.f[:], _.a, c=_.b.c, suffix='_c'), tester)), result)


if __name__ == '__main__':
    unittest.main()


# assertEqual
# assertNotEqual
# assertTrue
# assertFalse
# assertIs
# assertIsNot
# assertIsNone
# assertIsNotNone
# assertIn
# assertNotIn
# assertIsInstance
# assertIsNotInstance
