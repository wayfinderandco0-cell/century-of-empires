#!/usr/bin/env python3
"""Offline V162 tests: synthetic fixtures never imply visual approval."""
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import qa_v162_photo_boundary as seam

class BoundaryTests(unittest.TestCase):
    def test_local_texture(self):
        solid = Image.new('RGB', (100, 100), '#555555')
        self.assertEqual(seam.local_texture(solid, 50, 50), 0)
        checker = Image.new('RGB', (100, 100))
        p = checker.load()
        for y in range(100):
            for x in range(100):
                v = 255 if (x+y) % 2 else 0
                p[x, y] = (v, v, v)
        self.assertGreater(seam.local_texture(checker, 50, 50), 200)
        self.assertIsNone(seam.local_texture(checker, 2, 2))

    def test_polygon_samples_all_phone_layouts(self):
        for orientation, (w, h) in seam.VIEWPORTS.items():
            image = Image.new('RGB', (w*2, h*2), '#777777')
            records = seam.sample_image(image, orientation)
            self.assertGreaterEqual(len(records), 2)
            self.assertTrue(all(x['insideGradient'] == 0 and x['outsideGradient'] == 0 for x in records))
            self.assertTrue(all(0 <= x['edge'] < 8 for x in records))

    def test_bad_dpr_rejected(self):
        with self.assertRaisesRegex(ValueError, 'pixel ratio'):
            seam.sample_image(Image.new('RGB', (390, 844)), 'portrait')

    def test_missing_screenshot_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(FileNotFoundError, 'Missing real Matrei'):
                seam.audit(Path(td))

    def test_fails_if_source_changed(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'v161-native-material-study.html').write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'source changed'):
                seam.verify_preview(Path(td))

    def test_complete_four_config_audit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for engine in seam.ENGINES:
                for orientation, (w, h) in seam.VIEWPORTS.items():
                    Image.new('RGB', (w*2, h*2), '#777777').save(
                        root/f'{engine}-{orientation}-matrei-terrain.png')
            report = seam.audit(root)
            self.assertEqual(len(report['configurations']), 4)
            self.assertFalse(report['photoSeamApproved'])
            self.assertFalse(report['productionApproved'])
            self.assertFalse(report['bridgeBanksVerified'])
            self.assertTrue(all(v['meanOutsideToInside'] == 0
                                for v in report['configurations'].values()))

if __name__ == '__main__':
    unittest.main()
