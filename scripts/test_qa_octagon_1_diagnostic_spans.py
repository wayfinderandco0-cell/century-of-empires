"""Pure synthetic diagnostic tests; none validate road existence."""
import unittest
from qa_octagon_1_diagnostic_spans import low_contrast_runs


def rows(values):
    return [dict(sample=i, x=i * 16, y=200,
                 raw_cross_track_contrast=v) for i, v in enumerate(values)]


class DiagnosticSpanTests(unittest.TestCase):
    def test_flat_stretch_reports_exact_sample_positions(self):
        got = low_contrast_runs(rows([25, 12, 9, 8, 24, 3, 2, 1]))
        self.assertEqual([(r["start_sample"], r["end_sample"]) for r in got], [(1, 3), (5, 7)])
        self.assertEqual(got[0]["start_xy"], [16, 200])
        self.assertEqual(got[0]["end_xy"], [48, 200])
        self.assertEqual(got[0]["minimum_contrast"], 8)

    def test_boundary_and_missing_pixel_break_runs(self):
        self.assertEqual(low_contrast_runs(rows([18, 17, 17, None, 17, 17, 17])),
                         [dict(start_sample=4, end_sample=6, sample_count=3,
                               start_xy=[64, 200], end_xy=[96, 200],
                               minimum_contrast=17, maximum_contrast=17)])

    def test_missing_sample_index_does_not_bridge_gap(self):
        data = rows([4, 4, 4, 4, 4, 4])
        data[3]["sample"] = 8
        data[4]["sample"] = 9
        data[5]["sample"] = 10
        self.assertEqual(len(low_contrast_runs(data)), 2)

    def test_no_approval_claim_and_high_contrast(self):
        self.assertEqual(low_contrast_runs(rows([30, 40, 50, 60])), [])
        self.assertFalse(any("verified" in key or "traversable" in key
                             for result in low_contrast_runs(rows([1, 1, 1]))
                             for key in result))

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            low_contrast_runs(rows([1]), threshold=float("nan"))
        with self.assertRaises(ValueError):
            low_contrast_runs(rows([1]), minimum_samples=0)
        data = rows([1, 1, 1]); data[1]["sample"] = 0
        with self.assertRaises(ValueError):
            low_contrast_runs(data)


if __name__ == "__main__":
    unittest.main()
