#!/usr/bin/env python3
"""Synthetic checks; no assertion here certifies a historical road."""
import sys
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_octagon_1_raw_road import extract, samples, inspect

class RawRoadEvidenceTests(unittest.TestCase):
    def test_extract_requires_sourced_polyline(self):
        self.assertEqual(extract("const BASE_EAST=[[1,2],[3,4]];", "BASE_EAST"), [[1,2],[3,4]])
        with self.assertRaises(ValueError):
            extract("const BASE_EAST=[[1,2],[1200,4]];", "BASE_EAST")
        with self.assertRaises(ValueError):
            extract("const SOUTH=[];", "SOUTH")

    def test_samples_include_endpoints_without_artificial_loop(self):
        pts=list(samples([[100,100],[200,100]],16))
        self.assertEqual((pts[0][1],pts[0][2]), (100,100))
        self.assertEqual((round(pts[-1][1]),round(pts[-1][2])), (200,100))
        self.assertTrue(all(pts[i][1] < pts[i+1][1] for i in range(len(pts)-1)))

    def test_independent_raw_pixel_contrast(self):
        raw=Image.new('RGB',(1100,842),(40,110,50))
        flat=inspect(raw,[[100,400],[400,400]])
        self.assertTrue(all(r['raw_cross_track_contrast']==0 for r in flat))
        painted=raw.copy()
        ImageDraw.Draw(painted).line([(100,400),(400,400)], fill=(170,145,110), width=8)
        measured=inspect(painted,[[100,400],[400,400]])
        self.assertGreater(sum(r['raw_cross_track_contrast'] for r in measured)/len(measured),60)
        # Cross-track sampling must never turn into a production approval flag.
        self.assertNotIn('production_ready', measured[0])

if __name__ == '__main__':
    unittest.main()
