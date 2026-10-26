#!/usr/bin/env python3
"""V206 offline controls: source identity, exact crop RGB and false approvals."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import v204_contiguous_matrei_sources as source
import v206_audited_natural_cover as audit


class NativeCandidateTests(unittest.TestCase):
    def synthetic_source(self, folder):
        manifest = source.plan("forest")
        for panel in manifest["panels"]:
            for tile in panel["tiles"]:
                x, y, _ = tile["tileXYZ"]
                im = Image.new("RGB", (256, 256),
                               ((x * 17) % 150 + 35, (y * 13) % 150 + 35, 75))
                path = folder / tile["name"]
                im.save(path, "JPEG", quality=92)
                tile["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                tile["byteCount"] = path.stat().st_size
        source.render(manifest, folder)
        return {p["name"]: p["sourceSha256"] for p in manifest["panels"]}

    def test_crop_boxes_are_inside_native_panels_and_distinct(self):
        self.assertEqual(set(audit.RECTS), set(audit.SOURCE_SHA256))
        self.assertEqual(len(set(audit.RECTS.values())), 3)
        for x0, y0, x1, y1 in audit.RECTS.values():
            self.assertEqual((x1 - x0, y1 - y0), (96, 96))
            self.assertTrue(0 <= x0 < x1 <= 512 and 0 <= y0 < y1 <= 512)
        self.assertEqual(audit.FALSE_FLAGS[0], "gameArtApproved")

    def test_source_pins_exact_rgb_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "source"
            out = Path(td) / "candidate"
            src.mkdir()
            source_hashes = self.synthetic_source(src)
            # Test fixtures are synthetic, so substitute their hashes ONLY in
            # this isolated unit test; the production pins remain unchanged.
            with patch.dict(audit.SOURCE_SHA256, source_hashes):
                m = audit.build(src, out)
                self.assertTrue(audit.verify(src, out))
                self.assertEqual(len(m["candidates"]), 3)
                self.assertTrue(all(m[k] is False for k in audit.FALSE_FLAGS))
                self.assertTrue(all(p["sourceSiteNotV123GameCell"]
                                    for p in m["candidates"]))
                candidate = out / m["candidates"][0]["candidateImage"]
                with Image.open(candidate) as im:
                    changed = im.convert("RGB")
                changed.putpixel((1, 1), (255, 0, 0))
                changed.save(candidate)
                with self.assertRaises(ValueError):
                    audit.verify(src, out)
                audit.build(src, out)
                m = json.loads((out / "manifest.json").read_text())
                m["gameArtApproved"] = True
                (out / "manifest.json").write_text(json.dumps(m))
                with self.assertRaises(ValueError):
                    audit.verify(src, out)

    def test_changed_source_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "source"
            out = Path(td) / "candidate"
            src.mkdir()
            source_hashes = self.synthetic_source(src)
            with self.assertRaises(ValueError):
                audit.build(src, out)  # Synthetic image does not match real V205 pins.
            with patch.dict(audit.SOURCE_SHA256, source_hashes):
                audit.build(src, out)
                manifest = json.loads((src / "manifest.json").read_text())
                manifest["site"] = "matrei"
                (src / "manifest.json").write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    audit.verify(src, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
