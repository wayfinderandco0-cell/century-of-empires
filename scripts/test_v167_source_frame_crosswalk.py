#!/usr/bin/env python3
"""V167 source coordinate crosswalk tests; no game landmarks asserted."""
import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from PIL import Image

import v167_source_frame_crosswalk as v167

ROOT = Path(__file__).resolve().parents[1]


class SourceFrameCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v97 = json.loads((ROOT / "terrain-v97/manifest.json").read_text())
        cls.v102 = json.loads((ROOT / "terrain-v102/manifest.json").read_text())

    def test_actual_broad_and_narrow_sources_are_not_conflated(self):
        extents = v167.source_specs(self.v97, self.v102)
        self.assertEqual(extents["broad"], tuple(self.v97["boundsLonLat"]))
        self.assertEqual(extents["narrow"], tuple(self.v102["boundsLonLat"]))
        self.assertNotEqual(extents["broad"], extents["narrow"])
        # Identical pixel coordinates in two different source images
        # do NOT denote the same geographic place.
        a = v167.pixel_to_lonlat(768, 768, (1536, 1536), extents["broad"])
        n = v167.pixel_to_lonlat(768, 768, (2048, 2048), extents["narrow"])
        self.assertGreater(math.dist(a, n), 0.01)

    def test_actual_source_raster_dimensions(self):
        for name, (path, expected, scope) in v167.SOURCES.items():
            with self.subTest(source=name), Image.open(ROOT / path) as im:
                self.assertEqual(im.format, "WEBP")
                self.assertEqual(im.size, expected)
                self.assertIn(scope, ("broad", "narrow"))

    def test_all_source_pixel_geo_roundtrips(self):
        extents = v167.source_specs(self.v97, self.v102)
        for name, (_, size, scope) in v167.SOURCES.items():
            for xy in ((0, 0), (size[0]-1, size[1]-1),
                       (size[0]/3, size[1]/4), (size[0]/2, size[1]/2)):
                with self.subTest(source=name, xy=xy):
                    geo = v167.pixel_to_lonlat(*xy, size, extents[scope])
                    recovered = v167.lonlat_to_pixel(*geo, size, extents[scope])
                    self.assertLess(math.dist(xy, recovered), 1e-7)

    def test_north_up_orientation(self):
        b = v167.source_specs(self.v97, self.v102)["broad"]
        northwest = v167.pixel_to_lonlat(0, 0, (1536, 1536), b)
        southeast = v167.pixel_to_lonlat(1535, 1535, (1536, 1536), b)
        self.assertEqual(northwest, (b[0], b[3]))
        self.assertEqual(southeast, (b[2], b[1]))

    def test_reject_wrong_bounds(self):
        d = copy.deepcopy(self.v102)
        d["broadBoundsLonLat"] = d["boundsLonLat"]
        with self.assertRaisesRegex(ValueError, "BROAD bounds"):
            v167.source_specs(self.v97, d)

    def test_reject_reversed_bounds(self):
        d = copy.deepcopy(self.v97)
        d["boundsLonLat"][0], d["boundsLonLat"][2] = (
            d["boundsLonLat"][2], d["boundsLonLat"][0])
        with self.assertRaises(ValueError):
            v167.source_specs(d, self.v102)

    def test_reject_out_of_bounds_pixel_and_geography(self):
        b = v167.source_specs(self.v97, self.v102)["broad"]
        with self.assertRaisesRegex(ValueError, "outside source raster"):
            v167.pixel_to_lonlat(-1, 0, (1536, 1536), b)
        with self.assertRaisesRegex(ValueError, "outside source geography"):
            v167.lonlat_to_pixel(180, 90, (1536, 1536), b)

    def test_original_matrei_image_identity(self):
        html = (ROOT / "v121-octagon-1-painted-road.html").read_text()
        image = v167.original_matrei(html)
        self.assertEqual(image.size, (1536, 1024))
        with self.assertRaisesRegex(ValueError, "git blob changed"):
            v167.original_matrei(html + " ")

    def test_contact_sheets_and_report_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = v167.produce(ROOT, tmp)
            self.assertEqual(len(report["sourceFrames"]), 3)
            self.assertEqual(report["gameSourceTiePoints"], [])
            for key in ("gamePaintingGeographicallyRegistered",
                        "historicalRoadsVerified", "bridgeBanksVerified",
                        "westSouthGameArtComplete", "physicalIPhoneApproved",
                        "productionApproved"):
                self.assertIs(report[key], False)
            for name in [report["gamePaintingReviewSheet"]] + [
                    v["reviewSheet"] for v in report["sourceFrames"].values()]:
                with Image.open(Path(tmp) / name) as image:
                    self.assertEqual(image.format, "PNG")
                    self.assertGreater(image.width, 300)
                    self.assertGreater(image.height, 300)
            self.assertEqual(json.loads((Path(tmp) / "report.json").read_text()),
                             report)


if __name__ == "__main__":
    unittest.main()
