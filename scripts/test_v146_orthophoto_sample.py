#!/usr/bin/env python3
"""Offline deterministic V146 WMTS/provenance regressions."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).with_name("v146_orthophoto_sample.py")
spec = importlib.util.spec_from_file_location("sample", MODULE)
sample = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sample)


class GeographicSamples(unittest.TestCase):
    def setUp(self):
        self.source = {"boundsLonLat": [11.43, 47.075, 11.625, 47.19]}

    def test_points_in_geographic_extent_and_tile(self):
        p = sample.plan(self.source)
        self.assertEqual(len(p["samples"]), 3)
        for tile in p["samples"]:
            lon, lat = tile["pointLonLat"]
            west, south, east, north = tile["tileBoundsLonLat"]
            self.assertLessEqual(west, lon)
            self.assertLessEqual(lon, east)
            self.assertLessEqual(south, lat)
            self.assertLessEqual(lat, north)
            x, y, z = tile["tileXYZ"]
            self.assertEqual(tile["url"], f"{sample.BASE}/{z}/{y}/{x}.jpeg")
            self.assertTrue(tile["url"].startswith("https://mapsneu.wien.gv.at/"))

    def test_no_route_or_historical_certification(self):
        p = sample.plan(self.source)
        for flag in ("historic1780Certified", "gameRouteGeoregistered",
                     "gameOctagonCentersCertified", "productionApproved"):
            self.assertIs(p[flag], False)
        self.assertEqual(p["requiredAttribution"], "Datenquelle: basemap.at")
        self.assertEqual(p["license"], "CC BY 4.0")

    def test_invalid_extent_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside V102"):
            sample.plan({"boundsLonLat": [0, 0, 1, 1]})
        with self.assertRaisesRegex(ValueError, "Invalid V102"):
            sample.plan({"boundsLonLat": [11.8, 47.0, 11.2, 47.4]})

    def test_web_mercator_known_reference(self):
        self.assertEqual(sample.lonlat_to_xyz(0, 0, 1), (1, 1))
        self.assertEqual(sample.xyz_bounds(1, 1, 1),
                         [0.0, -85.0511287798066, 180.0, 0.0])
        for lon, lat in [(11.52, 47.13), (11.495, 47.14), (11.545, 47.12)]:
            for z in [8, 12, 17, 20]:
                x, y = sample.lonlat_to_xyz(lon, lat, z)
                w, s, e, n = sample.xyz_bounds(x, y, z)
                self.assertTrue(w <= lon <= e and s <= lat <= n)

    def test_out_of_projection_rejected(self):
        for lon, lat, z in [(0, 90, 17), (float("nan"), 0, 17), (0, 0, 21)]:
            with self.assertRaises(ValueError):
                sample.lonlat_to_xyz(lon, lat, z)


if __name__ == "__main__":
    unittest.main()
