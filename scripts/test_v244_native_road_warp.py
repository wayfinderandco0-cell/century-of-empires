#!/usr/bin/env python3
"""V244 regression and negative controls; NO artwork acceptance."""
import unittest
import numpy as np
from PIL import Image, ImageDraw
from v244_native_road_warp import register, validate_route

def sample_image():
    yy, xx = np.indices((1024, 1536))
    a = np.zeros((1024, 1536, 3), dtype=np.uint8)
    a[:, :, 0] = (xx // 5 + yy // 9) % 255
    a[:, :, 1] = (yy // 7 + 70) % 255
    a[:, :, 2] = (xx // 13 + 40) % 255
    image = Image.fromarray(a)
    ImageDraw.Draw(image).line(
        [(100, 400), (400, 400), (800, 420), (1200, 440), (1500, 440)],
        fill=(150, 95, 55), width=13)
    return image

class NativeWarpTests(unittest.TestCase):
    def test_whole_image_road_relocation_not_overlay(self):
        image = sample_image()
        source = [[100,400],[400,400],[800,420],[1200,440],[1500,440]]
        target = [[100,430],[400,435],[800,450],[1200,475],[1500,480]]
        out, report = register(image, source, target, sigma=145)
        self.assertLess(report['maxDisplacementPx'], 45)
        self.assertGreater(report['observedPixelCoverage'], .999)
        self.assertEqual(out.getpixel((400,435)), (150,95,55))
        self.assertNotEqual(out.getpixel((400,400)), (150,95,55))
        for flag in ('productionApproved', 'historicalRoadsVerified',
                     'bridgeBanksVerified', 'humanVisualApproval',
                     'sourceLicenseVerified'):
            self.assertIs(report[flag], False)

    def test_reject_large_deformation(self):
        with self.assertRaisesRegex(ValueError, 'displacement'):
            register(sample_image(),
                     [[100,200],[800,200],[1500,200]],
                     [[100,600],[800,600],[1500,600]])

    def test_reject_nonmonotonic_source_annotation(self):
        with self.assertRaisesRegex(ValueError, 'strictly increasing'):
            validate_route([[300,400],[200,400],[900,500]], 'source')

    def test_reject_south_vertical_northern_approach(self):
        with self.assertRaisesRegex(ValueError, 'strictly increasing'):
            register(sample_image(),
                     [[100,400],[800,420],[1500,440]],
                     [[466,0],[466,74],[700,400],[1270,605]])

    def test_reject_insufficient_road_coverage(self):
        with self.assertRaisesRegex(ValueError, 'does not cover'):
            register(sample_image(),
                     [[400,400],[800,420],[1300,440]],
                     [[200,400],[800,420],[1500,440]])

    def test_reject_missing_native_pixels(self):
        with self.assertRaisesRegex(ValueError, 'native image'):
            register(Image.new('RGB', (1200,800)),
                     [[100,400],[800,400],[1100,400]],
                     [[100,400],[800,400],[1100,400]])

    def test_detect_visible_road_beyond_survey_limit(self):
        source = [[0,400],[400,400],[800,420],[1200,440],[1536,440]]
        target = [[275,400],[400,400],[800,420],[1200,440],[1536,440]]
        _, report = register(sample_image(), source, target)
        self.assertEqual(report['extraRoadBeyondSurveyPx'], 275)
        self.assertFalse(report['visualRoadSurveyLimitPass'])

if __name__ == '__main__':
    unittest.main()
