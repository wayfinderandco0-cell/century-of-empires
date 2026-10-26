#!/usr/bin/env python3
"""V203 synthetic regression: missing/blurred images fail; matching images pass.

This is an image-algorithm unit test, NOT real source/period/human approval.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageFilter

SCRIPT = Path(__file__).with_name("qa_v203_canopy_structure.py")
spec = importlib.util.spec_from_file_location("v203", SCRIPT)
v203 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v203)


class CanopyTests(unittest.TestCase):
    def test_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            result = v203.audit(p, p / "report", make_contact=False)
            self.assertFalse(result["passed"])
            self.assertEqual(len(result["missing_screenshots"]), 12)
            self.assertFalse(result["humanArtApproved"])

    def test_blurred_neighbors_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            im = Image.new("RGB", (240, 320))
            pix = im.load()
            for y in range(320):
                for x in range(240):
                    t = (x * 17 + y * 29 + ((x * y) % 31) * 13) % 256
                    pix[x, y] = (t, (t * 3) % 256, (t * 7) % 256)
            for engine in v203.ENGINES:
                for orientation in v203.ORIENTATIONS:
                    for region in v203.REGIONS:
                        image = im if region == "matrei" else im.filter(ImageFilter.GaussianBlur(5))
                        image.save(p / f"{engine}-{orientation}-{region}-close.png")
            result = v203.audit(p, p / "report", make_contact=False)
            self.assertFalse(result["passed"])
            self.assertEqual(len(result["results"]), 4)
            self.assertTrue(all(not v["necessary_structure_gate_pass"] for v in result["results"].values()))

    def test_identical_art_can_pass_metric_but_never_approve(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            im = Image.new("RGB", (240, 320))
            pix = im.load()
            for y in range(320):
                for x in range(240):
                    t = (x * 17 + y * 29 + ((x * y) % 31) * 13) % 256
                    pix[x, y] = (t, (t * 3) % 256, (t * 7) % 256)
            for engine in v203.ENGINES:
                for orientation in v203.ORIENTATIONS:
                    for region in v203.REGIONS:
                        im.save(p / f"{engine}-{orientation}-{region}-close.png")
            result = v203.audit(p, p / "report", make_contact=False)
            self.assertTrue(result["passed"])
            for k in ("geographicRegistrationVerified", "periodSafeArtworkVerified", "humanArtApproved", "productionApproved"):
                self.assertFalse(result[k])


if __name__ == "__main__":
    unittest.main()
