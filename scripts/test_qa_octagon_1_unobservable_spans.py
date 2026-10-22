"""Synthetic-only tests: coverage does not establish a painted road."""
import unittest
from qa_octagon_1_unobservable_spans import unobservable_runs


def rows(values):
    return [dict(sample=i, x=100 + i * 16, y=200,
                 raw_cross_track_contrast=v) for i, v in enumerate(values)]


class UnobservableSpanTests(unittest.TestCase):
    def test_boundary_gaps_report_exact_positions(self):
        got = unobservable_runs(rows([None, None, 25, None, None]))
        self.assertEqual([(r["start_sample"], r["end_sample"]) for r in got],
                         [(0, 1), (3, 4)])
        self.assertEqual(got[0]["start_xy"], [100, 200])
        self.assertEqual(got[1]["end_xy"], [164, 200])
        self.assertEqual(got[1]["sample_count"], 2)

    def test_observed_flat_grass_is_not_missing(self):
        self.assertEqual(unobservable_runs(rows([0, 0, 0, 18, 40])), [])

    def test_skipped_indexes_never_bridge_gaps(self):
        data = rows([None, None, None])
        data[1]["sample"] = 5
        data[2]["sample"] = 6
        self.assertEqual(len(unobservable_runs(data)), 2)

    def test_invalid_index_or_coordinates_fail_closed(self):
        data = rows([None, None]); data[1]["sample"] = 0
        with self.assertRaises(ValueError):
            unobservable_runs(data)
        data = rows([None]); data[0]["x"] = float("nan")
        with self.assertRaises(ValueError):
            unobservable_runs(data)

    def test_invalid_contrast_fails_closed(self):
        for value in (float("nan"), -1, "unknown", True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                unobservable_runs(rows([value]))


if __name__ == "__main__":
    unittest.main()
