#!/usr/bin/env python3
"""V245 SOUTH native 2D remap controls. Synthetic images are diagnostics ONLY."""
import json
import os
from pathlib import Path
import unittest

import numpy as np
from PIL import Image, ImageDraw

from v245_south_2d_native_warp import register, polyline, diagnostic

SOUTH = [[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],
         [700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]]


def source_points(dx=18, dy=20):
    return [[x+dx,y+dy] for x,y in SOUTH]


def fixture():
    # Intentionally synthetic diagnostic, not game art or historic terrain.
    image = Image.new("RGB", (1536, 1024), (38, 92, 45))
    d = ImageDraw.Draw(image)
    d.line([tuple(p) for p in source_points()], fill=(135, 92, 61), width=16, joint="curve")
    d.line([tuple(p) for p in source_points()], fill=(168, 129, 86), width=3, joint="curve")
    return image


class South2DWarpTests(unittest.TestCase):
    def test_vertical_north_entry_and_real_pixel_relocation(self):
        original = fixture()
        out, report = register(original, source_points(), SOUTH)
        self.assertTrue(report["southNorthEdgeSupported"])
        self.assertGreater(report["originalPixelCoverage"], .997)
        self.assertGreater(report["minimumJacobian"], .24)
        self.assertLess(report["maximumDisplacementPx"], 30)
        self.assertGreater(out.getpixel((700,400))[0], 110)
        self.assertEqual(original.getpixel((700,400)), (38,92,45))
        for key in ("sourceLicenseVerified","sourceRegisteredToV123",
                    "historicalRoadsVerified","bridgeBanksVerified",
                    "v203VisualPass","fourBrowserPass","humanVisualApproval",
                    "productionApproved","promotionEligible"):
            self.assertIs(report[key], False)
        path = os.getenv("V245_DIAGNOSTIC_OUT")
        if path:
            p = Path(path);p.mkdir(parents=True, exist_ok=True)
            original.save(p/"synthetic-source-NOT-GAME-ART.png")
            diagnostic(out, SOUTH).save(p/"south-native-warp-overlay-NOT-GAME-ART.png")
            (p/"report.json").write_text(json.dumps(report, indent=2)+"\\n")

    def test_reject_large_displacement(self):
        with self.assertRaisesRegex(ValueError, "displacement"):
            register(fixture(), source_points(dx=0,dy=210), SOUTH)

    def test_reject_road_length_stretch(self):
        src = [[466,0],[466,900],[470,905],[800,910],[1270,920]]
        with self.assertRaisesRegex(ValueError, "arc-length ratio"):
            register(fixture(), src, SOUTH)

    def test_reject_invalid_trace_and_native_pixels(self):
        with self.assertRaisesRegex(ValueError, "sub-3px"):
            polyline([[466,0],[466,1],[470,160]], "source")
        with self.assertRaisesRegex(ValueError, "out-of-bounds"):
            polyline([[466,0],[500,-1],[1270,605]], "source")
        with self.assertRaisesRegex(ValueError, "native"):
            register(Image.new("RGB",(900,900)),source_points(),SOUTH)

    def test_north_entry_is_not_a_horizontal_x_monotone_shortcut(self):
        self.assertEqual(SOUTH[0], [466,0])
        self.assertEqual(SOUTH[1][0], SOUTH[0][0])
        out, report = register(fixture(), source_points(dx=0,dy=0), SOUTH)
        self.assertEqual(report["maximumDisplacementPx"], 0)
        self.assertEqual(out.size, (1536,1024))
        self.assertFalse(report["promotionEligible"])


if __name__ == "__main__":
    unittest.main()
