#!/usr/bin/env python3
"""Offline, fail-closed V147 source-grid and pixel-stitch tests."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
spec = importlib.util.spec_from_file_location("mosaic", Path(__file__).with_name("v147_orthophoto_mosaic.py"))
mosaic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mosaic)


class AdjacentSourceMosaic(unittest.TestCase):
    def setUp(self):
        self.manifest = mosaic.plan_grid({"boundsLonLat": [11.43, 47.075, 11.625, 47.19]})

    def test_exact_adjacent_xyz_and_extent(self):
        mosaic.validate_grid(self.manifest)
        self.assertEqual(self.manifest["grid"], [3, 3])
        self.assertEqual(self.manifest["pixelDimensions"], [768, 768])
        for r in range(3):
            for c in range(3):
                s = self.manifest["samples"][r * 3 + c]
                self.assertEqual((s["gridRow"], s["gridCol"]), (r, c))
                if c < 2:
                    right = self.manifest["samples"][r * 3 + c + 1]
                    self.assertEqual(s["tileBoundsLonLat"][2], right["tileBoundsLonLat"][0])
                if r < 2:
                    below = self.manifest["samples"][(r + 1) * 3 + c]
                    self.assertEqual(s["tileBoundsLonLat"][1], below["tileBoundsLonLat"][3])

    def test_no_unverified_historical_or_game_claims(self):
        for flag in ("historic1780Certified", "gameRouteGeoregistered",
                     "gameOctagonCentersCertified", "navigableRouteCertified",
                     "productionApproved"):
            self.assertIs(self.manifest[flag], False)
        self.assertEqual(self.manifest["requiredAttribution"], "Datenquelle: basemap.at")

    def test_rejects_missing_or_swapped_geographic_tile(self):
        self.manifest["samples"][0]["tileXYZ"][0] += 1
        with self.assertRaisesRegex(ValueError, "adjacency"):
            mosaic.validate_grid(self.manifest)

    def test_rejects_untrusted_tile_url(self):
        self.manifest["samples"][0]["url"] = "https://example.org/imaginary.jpeg"
        with self.assertRaisesRegex(ValueError, "Unrecognized"):
            mosaic.validate_grid(self.manifest)

    def test_rejects_outside_source_bounds(self):
        with self.assertRaisesRegex(ValueError, "exceeds V102"):
            mosaic.plan_grid({"boundsLonLat": [11.519, 47.129, 11.521, 47.131]})

    def test_stitch_is_exact_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            colors = {}
            for s in self.manifest["samples"]:
                r, c = s["gridRow"], s["gridCol"]
                color = (30 + 55 * c, 20 + 60 * r, 75 + 8 * (r + c))
                filename = s["name"] + ".jpeg"
                path = root / filename
                Image.new("RGB", (256, 256), color).save(path, "JPEG", quality=95)
                s["imageFile"] = filename
                s["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                colors[(r, c)] = Image.open(path).convert("RGB").getpixel((128, 128))
            out, diagnostics = mosaic.assemble(self.manifest, root)
            self.assertEqual(out.size, (768, 768))
            self.assertEqual(len(diagnostics), 12)
            for r in range(3):
                for c in range(3):
                    self.assertEqual(out.getpixel((c * 256 + 128, r * 256 + 128)),
                                     colors[(r, c)])
            (root / "r0c0.jpeg").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                mosaic.assemble(self.manifest, root)

    def test_rejects_missing_image_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Missing verified"):
                mosaic.assemble(self.manifest, Path(tmp))


if __name__ == "__main__":
    unittest.main()
