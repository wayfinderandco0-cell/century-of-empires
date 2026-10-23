#!/usr/bin/env python3
"""Synthetic tests of pixel audit, not historical road or bridge evidence."""
import importlib.util
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit_v127_road_pixels.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class RoadPixelAuditTests(unittest.TestCase):
    def setUp(self):
        self.img = Image.new('RGB', (200, 140), (42, 110, 42))
        self.route = [[20, 70], [180, 70]]

    def test_painted_contrast(self):
        ImageDraw.Draw(self.img).line(self.route, fill=(190, 170, 130), width=11)
        vals = [audit.evaluate_sample(self.img, p) for p in audit.sample_polyline(self.route)]
        self.assertTrue(all(v is not None and v['minRgbDelta'] > 90 for v in vals))
        self.assertEqual(audit.weak_spans(vals), [])

    def test_unpainted_path_flags_weak_evidence(self):
        vals = [audit.evaluate_sample(self.img, p) for p in audit.sample_polyline(self.route)]
        self.assertEqual(len(audit.weak_spans(vals)), 1)
        self.assertTrue(all(v['minRgbDelta'] == 0 for v in vals))

    def test_normal_rotates_with_path(self):
        ImageDraw.Draw(self.img).line([(100, 10), (100, 130)], fill=(190, 170, 130), width=11)
        vals = [audit.evaluate_sample(self.img, p) for p in audit.sample_polyline([[100, 10], [100, 130]])]
        self.assertTrue(all(v['minRgbDelta'] > 90 for v in vals))

    def test_out_of_image_samples_are_not_extrapolated(self):
        vals = [audit.evaluate_sample(self.img, p) for p in audit.sample_polyline([[0, 5], [180, 5]])]
        self.assertTrue(any(v is None for v in vals))

    def test_bad_geometry_rejected(self):
        for route in ([[0, 0]], [[0, 0], [float('nan'), 1]], [[1, 1], [1, 1]], [[True, 2], [3, 4]]):
            with self.assertRaises(ValueError):
                list(audit.sample_polyline(route))

    def test_bridge_not_certified_by_painted_contrast(self):
        ImageDraw.Draw(self.img).line(self.route, fill=(190, 170, 130), width=11)
        manifest = {'dimensions': {'width': 200, 'height': 140},
                    'art': {'path': 'synthetic'},
                    'movement': {'roads': {'bridge': [[20, 70], [50, 70], [150, 70], [180, 70]]},
                                 'primaryStoneBridgeEnds': [[50, 70], [150, 70]]}}
        result = audit.audit(self.img, manifest)
        self.assertFalse(result['bridge']['riverCrossingVerified'])
        self.assertFalse(result['pixelAlignmentVerified'])
        self.assertFalse(result['productionEnabled'])

    def test_wrong_source_dimensions_rejected(self):
        with self.assertRaises(ValueError):
            audit.audit(self.img, {'dimensions': {'width': 100, 'height': 100}})


if __name__ == '__main__':
    unittest.main()
