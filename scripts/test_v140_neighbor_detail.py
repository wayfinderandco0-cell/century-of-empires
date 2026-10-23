#!/usr/bin/env python3
"""Synthetic regression for V140 detail parity, not art approval."""
import unittest
from PIL import Image
from qa_v140_neighbor_detail import assess, detail_score

class NeighborVisualGateTests(unittest.TestCase):
    def test_flat_neighbor_rejected(self):
        flat = detail_score(Image.new("RGB", (160, 120), (80, 110, 80)))
        high = Image.new("RGB", (160, 120))
        for y in range(120):
            for x in range(160):
                c = 20 if (x // 3 + y // 3) % 2 else 225
                high.putpixel((x, y), (c, c, c))
        textured = detail_score(high)
        checks = assess({"matrei": textured, "west": flat, "south": textured})
        self.assertFalse(checks["west"]["passes_minimum_detail"])
        self.assertTrue(checks["south"]["passes_minimum_detail"])

    def test_equally_detailed_tiles_pass_minimum_only(self):
        s = {"mean_luma_gradient": 10.0, "strong_edge_fraction": .2}
        self.assertTrue(all(c["passes_minimum_detail"] for c in assess({"matrei": s, "west": s, "south": s}).values()))

    def test_borderline_neighbor_rejected(self):
        matrei = {"mean_luma_gradient": 20.0, "strong_edge_fraction": .4}
        west = {"mean_luma_gradient": 6.0, "strong_edge_fraction": .08}
        south = {"mean_luma_gradient": 8.0, "strong_edge_fraction": .2}
        c = assess({"matrei": matrei, "west": west, "south": south})
        self.assertFalse(c["west"]["passes_minimum_detail"])
        self.assertTrue(c["south"]["passes_minimum_detail"])

    def test_small_image_rejected(self):
        with self.assertRaises(ValueError):
            detail_score(Image.new("RGB", (10, 10)))

if __name__ == "__main__":
    unittest.main()
