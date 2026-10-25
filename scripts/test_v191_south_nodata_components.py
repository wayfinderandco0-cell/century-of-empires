#!/usr/bin/env python3
"""V191 small, deterministic source-mask topology and tamper checks."""
import sys
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v191_south_nodata_components as v191


def fixture():
    source = Image.new('RGB', (12, 9), (42, 91, 51))
    overlay = Image.new('RGBA', (12, 9), (0, 0, 0, 0))
    def candidate(x, y):
        source.putpixel((x, y), (255, 255, 255))
        overlay.putpixel((x, y), (22, 91, 62, 255))
    for p in ((5, 6), (5, 7), (5, 8), (6, 8), (7, 8), (7, 7)):
        candidate(*p)
    for p in ((2, 2), (2, 3), (3, 3)):
        candidate(*p)
    for p in ((0, 5), (1, 5)):
        candidate(*p)
    source.putpixel((10, 1), (253, 253, 253))
    return source, overlay


class CandidateConnectivityTests(unittest.TestCase):
    def test_regions_are_disjoint_and_preserve_source(self):
        original, overlay = fixture()
        source_bytes, overlay_bytes = original.tobytes(), overlay.tobytes()
        result = v191.classify(original, overlay)
        self.assertEqual(result['candidatePixels'], 11)
        self.assertEqual(result['originalNearWhitePixels'], 12)
        self.assertEqual(result['unresolvedOriginalNearWhitePixels'], 1)
        self.assertEqual(result['componentCount'], 3)
        self.assertEqual(result['classification']['south-edge'], {'components': 1, 'pixels': 6})
        self.assertEqual(result['classification']['other-edge'], {'components': 1, 'pixels': 2})
        self.assertEqual(result['classification']['interior'], {'components': 1, 'pixels': 3})
        self.assertEqual(original.tobytes(), source_bytes)
        self.assertEqual(overlay.tobytes(), overlay_bytes)
        self.assertEqual(result['mask'].getpixel((10, 1)), (0, 0, 0, 0))
        self.assertEqual(result['mask'].getpixel((5, 8)), v191.COLORS['south-edge'])
        self.assertEqual(result['mask'].getpixel((2, 2)), v191.COLORS['interior'])

    def test_four_neighbors_do_not_connect_diagonal_snow(self):
        source = Image.new('RGB', (4, 4), (40, 80, 30))
        overlay = Image.new('RGBA', (4, 4), (0, 0, 0, 0))
        for p in ((0, 3), (1, 2)):
            source.putpixel(p, (255, 255, 255))
            overlay.putpixel(p, (30, 60, 90, 255))
        result = v191.classify(source, overlay)
        self.assertEqual(result['componentCount'], 2)
        self.assertEqual(result['classification']['south-edge']['pixels'], 1)
        self.assertEqual(result['classification']['interior']['pixels'], 1)

    def test_reject_overlay_on_observed_terrain(self):
        source, overlay = fixture()
        overlay.putpixel((9, 4), (25, 40, 80, 255))
        with self.assertRaisesRegex(ValueError, 'overwrites observed'):
            v191.classify(source, overlay)

    def test_reject_fractional_alpha(self):
        source, overlay = fixture()
        overlay.putpixel((2, 2), (25, 40, 80, 128))
        with self.assertRaisesRegex(ValueError, 'fractional'):
            v191.classify(source, overlay)

    def test_reject_fake_white_replacement(self):
        source, overlay = fixture()
        overlay.putpixel((2, 2), (255, 255, 255, 255))
        with self.assertRaisesRegex(ValueError, 'contains white'):
            v191.classify(source, overlay)

    def test_reject_wrong_dimensions_or_color_mode(self):
        source, overlay = fixture()
        with self.assertRaises(ValueError):
            v191.classify(source, Image.new('RGBA', (5, 5)))
        with self.assertRaises(ValueError):
            v191.classify(source.convert('RGBA'), overlay)


if __name__ == '__main__':
    unittest.main()
