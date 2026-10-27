#!/usr/bin/env python3
"""V232 negative controls: semantic cartway clearance is necessary, never approval."""
import unittest
from PIL import Image, ImageDraw
from v232_route_ground_preflight import (
    FALSE_FLAGS, SIZE, inspect, source_roads,
)

class RouteGroundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roads = source_roads()

    def test_exact_v123_road_vertices(self):
        self.assertEqual(len(self.roads["west"]), 13)
        self.assertEqual(len(self.roads["south"]), 12)
        self.assertEqual(self.roads["west"][0], [1536, 478])
        self.assertEqual(self.roads["south"][0], [466, 0])

    def test_open_grass_is_necessary_not_approval(self):
        meadow = Image.new("RGB", SIZE, (136, 150, 88))
        for tile, points in self.roads.items():
            report, _ = inspect(meadow, points, tile)
            self.assertTrue(report["necessaryRoadGroundGate"])
            for key in FALSE_FLAGS:
                self.assertFalse(report[key])

    def test_forest_crossing_is_rejected(self):
        meadow = Image.new("RGB", SIZE, (136, 150, 88))
        draw = ImageDraw.Draw(meadow)
        draw.line([tuple(p) for p in self.roads["west"]],
                  fill=(20, 45, 26), width=90, joint="curve")
        report, _ = inspect(meadow, self.roads["west"], "west")
        self.assertFalse(report["necessaryRoadGroundGate"])
        self.assertGreater(report["darkCanopyArea"], 0.7)

    def test_rock_crossing_is_rejected(self):
        rock = Image.new("RGB", SIZE, (152, 152, 152))
        report, _ = inspect(rock, self.roads["south"], "south")
        self.assertFalse(report["necessaryRoadGroundGate"])
        self.assertGreater(report["bareRockArea"], 0.9)

    def test_mutated_immutable_road_rejected(self):
        from pathlib import Path
        source = Path(__file__).resolve().parents[1]/"terrain-grid/v123-atlas.js"
        text = source.read_text()
        with self.assertRaisesRegex(ValueError, "endpoints changed"):
            source_roads(text.replace("[1536,478]", "[1535,478]", 1))

    def test_wrong_image_size_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected"):
            inspect(Image.new("RGB", (512, 512)), self.roads["west"], "west")

if __name__ == "__main__":
    unittest.main()
