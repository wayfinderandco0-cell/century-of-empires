#!/usr/bin/env python3
"""V207 fail-closed tests: source RGB untouched; visible modern pixels excluded."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import v204_contiguous_matrei_sources as source
import v206_audited_natural_cover as v206
import v207_conservative_modern_masks as masks

class SourceMaskTests(unittest.TestCase):
    def make_fixture(self, folder):
        manifest = source.plan("forest")
        for panel in manifest["panels"]:
            for tile in panel["tiles"]:
                x, y, _ = tile["tileXYZ"]
                image = Image.new("RGB", (256, 256),
                                  ((x * 17) % 150 + 35, (y * 13) % 150 + 35, 75))
                path = folder / tile["name"]
                image.save(path, "JPEG", quality=92)
                tile["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                tile["byteCount"] = path.stat().st_size
        source.render(manifest, folder)
        return {p["name"]: p["sourceSha256"] for p in manifest["panels"]}

    def test_known_visible_modern_and_retained_control_points(self):
        self.assertEqual(set(masks.ANNOTATIONS), set(v206.SOURCE_SHA256))
        self.assertIn("gameArtApproved", masks.FALSE_FLAGS)
        for name, annotation in masks.ANNOTATIONS.items():
            image = masks.mask_for(name)
            self.assertEqual(image.mode, "L")
            self.assertEqual(image.size, (512, 512))
            for xy in annotation["knownExcluded"]:
                self.assertEqual(image.getpixel(tuple(xy)), 0, (name, xy))
            for xy in annotation["knownRetained"]:
                self.assertEqual(image.getpixel(tuple(xy)), 255, (name, xy))
            self.assertGreater(len(annotation["knownExcluded"]), 0)

    def test_native_rgb_exact_and_tampering_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp) / "source", Path(tmp) / "candidate"
            src.mkdir()
            hashes = self.make_fixture(src)
            with patch.dict(v206.SOURCE_SHA256, hashes):
                report = masks.build(src, out)
                self.assertTrue(masks.verify(src, out))
                self.assertEqual(len(report["panels"]), 3)
                self.assertTrue(all(report[k] is False for k in masks.FALSE_FLAGS))
                panel = report["panels"][0]
                with Image.open(src / (panel["name"] + ".png")) as original:
                    expected_rgb = original.convert("RGB").tobytes()
                with Image.open(out / panel["candidateImage"]) as candidate:
                    self.assertEqual(candidate.convert("RGB").tobytes(), expected_rgb)
                mask_path = out / panel["maskImage"]
                with Image.open(mask_path) as im:
                    altered = im.copy()
                altered.putpixel((400, 450), 0)
                altered.save(mask_path)
                with self.assertRaises(ValueError):
                    masks.verify(src, out)
                masks.build(src, out)
                contact = out / "v207-exclusion-contact.png"
                with Image.open(contact) as im:
                    tampered = im.copy()
                tampered.putpixel((0, 0), (255, 255, 255))
                tampered.save(contact)
                with self.assertRaises(ValueError):
                    masks.verify(src, out)

    def test_false_approval_and_source_substitution_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp) / "source", Path(tmp) / "candidate"
            src.mkdir()
            hashes = self.make_fixture(src)
            with self.assertRaises(ValueError):
                masks.build(src, out)  # Synthetic fixture does not match real V205 pins.
            with patch.dict(v206.SOURCE_SHA256, hashes):
                masks.build(src, out)
                report = json.loads((out / "manifest.json").read_text())
                report["periodSafe"] = True
                (out / "manifest.json").write_text(json.dumps(report))
                with self.assertRaises(ValueError):
                    masks.verify(src, out)
                masks.build(src, out)
                report = json.loads((src / "manifest.json").read_text())
                report["site"] = "matrei"
                (src / "manifest.json").write_text(json.dumps(report))
                with self.assertRaises(ValueError):
                    masks.verify(src, out)

if __name__ == "__main__":
    unittest.main(verbosity=2)
