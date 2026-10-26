#!/usr/bin/env python3
"""V214 negative controls: no masked pixels, image substitution or false approvals."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

import v204_contiguous_matrei_sources as source
import v206_audited_natural_cover as v206
import v214_source_native_material_bank as bank


class NativeMaterialTests(unittest.TestCase):
    def test_selects_unmasked_native_detail_without_resizing(self):
        image = Image.new("RGB", (256, 256), (50, 60, 40))
        draw = ImageDraw.Draw(image)
        for x in range(0, 256, 4):
            draw.line((x, 0, x, 255), fill=(90 + x % 100, 130, 60), width=2)
        mask = Image.new("L", (256, 256), 255)
        ImageDraw.Draw(mask).rectangle((0, 0, 126, 255), fill=0)
        box, score = bank.choose_native_patch(image, mask, size=64, margin=8, step=8)
        self.assertGreaterEqual(box[0], 135)
        self.assertEqual(box[2] - box[0], 64)
        self.assertEqual(box[3] - box[1], 64)
        self.assertGreater(score, 0)
        self.assertEqual(mask.crop(box).getextrema(), (255, 255))

    def test_no_clear_area_and_invalid_masks_fail_closed(self):
        image = Image.new("RGB", (256, 256), (30, 70, 40))
        self.assertRaises(ValueError, bank.choose_native_patch,
                          image, Image.new("L", (256, 256), 0), 64, 8, 8)
        self.assertRaises(ValueError, bank.choose_native_patch,
                          image, Image.new("L", (256, 256), 128), 64, 8, 8)
        self.assertRaises(ValueError, bank.choose_native_patch,
                          image, Image.new("L", (128, 256), 255), 64, 8, 8)

    def test_inspected_date_imprint_quarantined_before_selection(self):
        self.assertEqual(bank.reviewed_mask("west_reference").getpixel((370, 60)), 0)
        self.assertEqual(bank.reviewed_mask("west_reference").getpixel((390, 80)), 0)
        self.assertEqual(bank.reviewed_mask("matrei_reference").getpixel((300, 420)), 255)
        self.assertRaises(ValueError, bank.reviewed_mask, "unknown_panel")

    @staticmethod
    def fixture(folder):
        manifest = source.plan("forest")
        for panel in manifest["panels"]:
            for tile in panel["tiles"]:
                im = Image.new("RGB", (256, 256), (45, 77, 48))
                d = ImageDraw.Draw(im)
                for x in range(0, 256, 8):
                    d.line((x, 0, x, 255), fill=(90 + x % 100, 125, 68), width=3)
                path = folder / tile["name"]
                im.save(path, "JPEG", quality=93)
                tile["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                tile["byteCount"] = path.stat().st_size
        source.render(manifest, folder)
        return {p["name"]: p["sourceSha256"] for p in manifest["panels"]}

    def test_source_provenance_exact_pixels_and_tampering(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            src, out = root / "source", root / "out"
            src.mkdir()
            hashes = self.fixture(src)
            with self.assertRaises(ValueError):
                bank.build(src, out)  # Synthetic source cannot impersonate pinned V205.
            with patch.dict(v206.SOURCE_SHA256, hashes):
                report = bank.build(src, out)
                self.assertTrue(bank.verify(src, out))
                self.assertEqual(len(report["candidates"]), 3)
                self.assertTrue(all(report[key] is False for key in bank.FALSE_FLAGS))
                for row in report["candidates"]:
                    self.assertEqual(len(row["nativeRectXYXY"]), 4)
                    self.assertFalse(row["geographicallyRegisteredToGame"])
                    self.assertFalse(row["periodSafeMaterial"])
                sample = out / report["candidates"][0]["image"]
                with Image.open(sample) as im:
                    altered = im.copy()
                altered.putpixel((0, 0), (255, 255, 255))
                altered.save(sample)
                with self.assertRaises(ValueError):
                    bank.verify(src, out)
                bank.build(src, out)
                manifest = json.loads((out / "manifest.json").read_text())
                manifest["gameArtApproved"] = True
                (out / "manifest.json").write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    bank.verify(src, out)
                bank.build(src, out)
                with Image.open(out / "v214-native-material-contact.png") as im:
                    contact = im.copy()
                contact.putpixel((0, 0), (255, 255, 255))
                contact.save(out / "v214-native-material-contact.png")
                with self.assertRaises(ValueError):
                    bank.verify(src, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
