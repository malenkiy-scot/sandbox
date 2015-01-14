__author__ = 'malenkiy_scot'

import unittest
import mytrace
import traced_for_test


class TestMyTrace(unittest.TestCase):
    def test_success(self):
        mytrace.trace_module("traced_for_test.py")

        traced_for_test.foo(1, 2, 'moo')
        traced_for_test.bar()
        traced_for_test.foo((4, 5), {})

        self.assertEquals(mytrace.num_calls("traced_for_test", "foo"), 2)
        self.assertEquals(mytrace.num_calls("traced_for_test", "bar"), 1)
        self.assertIsNone(mytrace.num_calls("traced_for_test", "moo"))
        self.assertIsNone(mytrace.num_calls("not_traced", "foo"))

if __name__ == '__main__':
    suite = unittest.makeSuite(TestMyTrace)
    unittest.TextTestRunner().run(suite)
