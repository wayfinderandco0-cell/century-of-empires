#!/usr/bin/env python3
"""Unit tests for the V189 fail-closed three-center phone-art gate."""
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_v189_three_center_art as gate


class ThreeCenterGateTests(unittest.TestCase):
    def test_v171_thresholds_preserved(self):
        self.assertEqual(gate.MIN_RELATIVE_GRADIENT, .35)
        self.assertEqual(gate.MIN_RELATIVE_STRONG_EDGES, .25)
        self.assertEqual(gate.ZOOM, 6.)

    def test_flat_west_rejected_even_when_south_passes(self):
        scores = {
            "matrei": {"mean_luma_gradient": 10., "strong_edge_fraction": .2},
            "west": {"mean_luma_gradient": 2., "strong_edge_fraction": .01},
            "south": {"mean_luma_gradient": 8., "strong_edge_fraction": .18},
        }
        checks = gate.assess(scores)
        self.assertFalse(checks["west"]["passes_minimum_detail"])
        self.assertTrue(checks["south"]["passes_minimum_detail"])

    def test_exact_threshold_is_accepted_as_minimum_not_art_approval(self):
        scores = {
            "matrei": {"mean_luma_gradient": 10., "strong_edge_fraction": .2},
            "west": {"mean_luma_gradient": 3.5, "strong_edge_fraction": .05},
            "south": {"mean_luma_gradient": 10., "strong_edge_fraction": .2},
        }
        self.assertTrue(all(c["passes_minimum_detail"] for c in gate.assess(scores).values()))

    def test_all_twelve_phone_captures_required(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.assertFalse(gate.audit(folder)["passed"])
            self.assertEqual(len(gate.audit(folder)["missing_screenshots"]), 12)
            for engine in gate.ENGINES:
                for orient, _, _ in gate.ORIENTATIONS:
                    for region in gate.REGIONS:
                        im = Image.new("RGB", (80, 80))
                        pixels = im.load()
                        for y in range(80):
                            for x in range(80):
                                c = 255 if (x + y) % 2 else 0
                                pixels[x, y] = (c, c, c)
                        im.save(folder / f"{engine}-{orient}-{region}-close.png")
            report = gate.audit(folder)
            self.assertTrue(report["passed"])
            self.assertFalse(report["productionApproved"])
            self.assertFalse(report["physicalIPhoneApproved"])
            self.assertFalse(report["westSouthGeographicallyRegistered"])
            (folder / "webkit-landscape-south-close.png").unlink()
            self.assertFalse(gate.audit(folder)["passed"])

    def test_tiny_screenshot_rejected(self):
        with self.assertRaises(ValueError):
            gate.detail_score(Image.new("RGB", (8, 8)))


if __name__ == "__main__":
    unittest.main()
