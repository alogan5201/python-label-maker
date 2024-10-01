import unittest
from python_label_maker import module1

class TestModule1(unittest.TestCase):
    def test_add_numbers(self):
        self.assertEqual(module1.add_numbers(2, 3), 5)
        self.assertEqual(module1.add_numbers(-1, 1), 0)
        self.assertEqual(module1.add_numbers(0, 0), 0)

    def test_multiply_numbers(self):
        self.assertEqual(module1.multiply_numbers(2, 3), 6)
        self.assertEqual(module1.multiply_numbers(-2, 3), -6)
        self.assertEqual(module1.multiply_numbers(0, 5), 0)

    def test_some_function(self):
        self.assertEqual(module1.some_function(), "Hello from module1!")

if __name__ == '__main__':
    unittest.main()