#!/usr/bin/env python3
"""V215 negative controls for native geography, seams, transparent exclusions."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

import v206_audited_natural_cover as v206
import v214_source_native_material_bank as bank
import v215_native_source_seam_atlas as atlas
from test_v214_source_native_material_bank import NativeMaterialTests


class NativeSeamAtlasTests(unittest.TestCase):
    def test_requires_both_sides_of_real_native_seam(self):
        a = Image.new("RGB", (512, 512), (50, 70, 40))
        b = Image.new("RGB", (512, 512), (52, 72, 42))
        m = Image.new("L", (512, 512), 255)
        info = atlas.seam_stats(a, b, m, m, "vertical")
        self.assertEqual(info["pairedNativePixels"], 512)
        self.assertEqual(info["meanSourceBoundaryDifferenceRGB"], 2)
        self.assertFalse(info["gameSeamOrRoadAlignmentVerified"])
        m.putpixel((0, 0), 0)
        self.assertEqual(atlas.seam_stats(a, b, m, m, "vertical")["pairedNativePixels"], 511)
        self.assertRaises(ValueError, atlas.seam_stats, a, b,
                          Image.new("L", (512, 512), 0), m, "horizontal")
        self.assertRaises(ValueError, atlas.seam_stats, a, b, m, m, "diagonal")

    def test_original_pixels_exclusions_and_approval_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            src, out = root / "source", root / "atlas"
            src.mkdir()
            hashes = NativeMaterialTests.fixture(src)
            # Unpinned synthetic fixture cannot impersonate inspected V205 imagery.
            with self.assertRaises(ValueError):
                atlas.build(src, out)
            with patch.dict(v206.SOURCE_SHA256, hashes):
                report = atlas.build(src, out)
                self.assertTrue(atlas.verify(src, out))
                self.assertEqual(report["sourceImagePixels"], [1024, 1024])
                self.assertEqual(len(report["nativePanels"]), 3)
                self.assertTrue(all(report[f] is False for f in atlas.FALSE_FLAGS))
                self.assertTrue(all(
                    row["pairedNativePixels"] >= 64
                    for row in report["nativeSourceSeamDiagnostics"].values()))
                path = out / report["sourceAtlasFile"]
                with Image.open(path) as im:
                    original = im.copy()
                self.assertEqual(original.mode, "RGBA")
                self.assertEqual(original.getpixel((0, 800)), (0, 0, 0, 0))
                self.assertEqual(original.getpixel((20, 25)), (0, 0, 0, 0))
                self.assertEqual(original.getpixel((512 + 90, 90)), (0, 0, 0, 0))
                self.assertEqual(original.getpixel((512 + 285, 512 + 125)), (0, 0, 0, 0))
                self.assertEqual(original.getpixel((512 + 300, 512 + 40))[3], 255)
                altered = original.copy()
                altered.putpixel((20, 25), (255, 0, 0, 255))
                altered.save(path)
                with self.assertRaises(ValueError):
                    atlas.verify(src, out)
                atlas.build(src, out)
                altered = original.copy()
                p = (512 + 300, 512 + 40)
                altered.putpixel(p, (0, 0, 0, 255))
                altered.save(path)
                with self.assertRaises(ValueError):
                    atlas.verify(src, out)
                atlas.build(src, out)
                manifest_path = out / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                manifest["sourceRegisteredToV123"] = True
                manifest_path.write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    atlas.verify(src, out)
                atlas.build(src, out)
                manifest = json.loads(manifest_path.read_text())
                manifest["nativeSourceSeamDiagnostics"]["westToMatrei"]["pairedNativePixels"] = 512
                manifest_path.write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    atlas.verify(src, out)
                atlas.build(src, out)
                image_path = out / report["reviewContactFile"]
                with Image.open(image_path) as im:
                    contact = im.copy()
                contact.putpixel((0, 0), (255, 255, 255))
                contact.save(image_path)
                with self.assertRaises(ValueError):
                    atlas.verify(src, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
