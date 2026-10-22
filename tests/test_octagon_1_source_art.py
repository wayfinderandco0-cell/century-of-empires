import unittest
from scripts.audit_octagon_1_source_art import sample

class RoadSamplingTests(unittest.TestCase):
    def test_arc_length(self):
        self.assertEqual(sample([[0, 0], [10, 0], [10, 30]], 0.5), [10, 10])
    def test_endpoints(self):
        route = [[699, 799], [717, 794], [1100, 704]]
        self.assertEqual(sample(route, 0), [699, 799])
        self.assertEqual(sample(route, 1), [1100, 704])

if __name__ == "__main__":
    unittest.main()
