#!/usr/bin/env python3
"""Regression and negative controls for art-composition constraints."""
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from v243_road_conditioning import (CLEARANCE_RADIUS, ROADBED_RADIUS,
                                    draw_masks, generate, load_routes)

WEST = [[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],[980,515],
        [890,535],[784,551],[680,560],[570,540],[470,520],[370,522],[275,550]]
SOUTH = [[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],
         [700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]]


def mock_atlas(west=WEST, south=SOUTH):
    return ('const westRoad=' + json.dumps(west, separators=(',', ':')) + ';\n'
            'const southRoad=' + json.dumps(south, separators=(',', ':')) + ';\n')


class ConditioningTests(unittest.TestCase):
    def test_route_masks_keep_exact_centerline(self):
        for points in (WEST, SOUTH):
            clear, road, octagon = draw_masks(points)
            self.assertEqual(clear.size, (1536, 1024))
            for x, y in points:
                px = min(x, 1535); py = min(y, 1023)
                self.assertEqual(clear.getpixel((px, py)), 255)
                self.assertEqual(road.getpixel((px, py)), 255)
            self.assertEqual(clear.getpixel((800, 950)), 0)
            self.assertEqual(road.getpixel((800, 950)), 0)
            self.assertEqual(octagon.getpixel((0, 0)), 0)
            self.assertEqual(octagon.getpixel((700, 500)), 255)

    def test_clearance_is_wider_than_roadbed(self):
        self.assertGreater(CLEARANCE_RADIUS, ROADBED_RADIUS * 3)
        clear, road, _ = draw_masks(WEST)
        self.assertEqual(clear.getpixel((980, 545)), 255)
        self.assertEqual(road.getpixel((980, 545)), 0)

    def test_reject_wrong_sha_and_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'v123.js'
            p.write_text(mock_atlas())
            with self.assertRaisesRegex(ValueError, 'blob changed'):
                load_routes(p)
            sha, routes = load_routes(p, require_pin=False)
            self.assertEqual(routes['west'], WEST)
            self.assertEqual(routes['south'], SOUTH)
            p.write_text(mock_atlas(west=WEST[:-1] + [[275, 552]]))
            with self.assertRaisesRegex(ValueError, 'portal drift'):
                load_routes(p, require_pin=False)

    def test_reject_out_of_bounds_and_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'v123.js'
            p.write_text(mock_atlas(south=SOUTH[:-2] + [[-1, 585], SOUTH[-1]]))
            with self.assertRaisesRegex(ValueError, 'outside native cell'):
                load_routes(p, require_pin=False)
            p.write_text('const westRoad=' + json.dumps(WEST) + ';')
            with self.assertRaisesRegex(ValueError, 'Missing immutable'):
                load_routes(p, require_pin=False)

    def test_both_guides_and_false_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'v123.js'; p.write_text(mock_atlas())
            report = generate(p, Path(tmp) / 'out', require_pin=False)
            self.assertEqual(set(report['cells']), {'west', 'south'})
            for flag in ('productionApproved', 'humanArtApproved', 'bridgeBanksVerified',
                         'sourceRegisteredToV123', 'historicRoadsVerified'):
                self.assertIs(report[flag], False)
            for tile in ('west', 'south'):
                with Image.open(Path(tmp)/'out'/f'{tile}-composition-guide.png') as img:
                    self.assertEqual(img.size, (1536, 1024))
                self.assertFalse(report['cells'][tile]['imageReadyForGameplay'])
            self.assertEqual(json.loads((Path(tmp)/'out'/'manifest.json').read_text())['version'],243)


if __name__ == '__main__':
    unittest.main()
