#!/usr/bin/env python3
"""V205: negative/positive checks for native, adjacent natural-cover SOURCE site."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import v204_contiguous_matrei_sources as source


class ForestMaterialSourceTests(unittest.TestCase):
    def test_distinct_anchored_forest_reference(self):
        matrei = source.plan("matrei")
        forest = source.plan("forest")
        self.assertNotEqual(matri := matrei["anchorLonLat"], forest["anchorLonLat"])
        self.assertEqual(matri, [11.45306, 47.13083])
        self.assertEqual(forest["anchorLonLat"], [11.4395, 47.1])
        self.assertIn("approximate", forest["anchorSource"])
        self.assertTrue(source.validate(forest))
        self.assertEqual(len({tuple(t["tileXYZ"]) for p in forest["panels"]
                              for t in p["tiles"]}), 12)
        for flag in source.FALSE_FLAGS:
            self.assertIs(forest[flag], False)
        source.verify_source_invariants("forest")

    def test_no_site_or_source_substitution(self):
        m = source.plan("forest")
        for changed in (
            {**m, "site": "matrei"},
            {**m, "anchorLonLat": [11.5, 47.2]},
            {**m, "productionApproved": True},
            {**m, "modernFeaturesFullyExcluded": True},
            {**m, "v123RoadsGeoregistered": True},
        ):
            with self.assertRaises(ValueError):
                source.validate(changed)
        self.assertRaises(ValueError, source.plan, "unknown")

    def test_forest_source_rgb_integrity(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            m = source.plan("forest")
            for p in m["panels"]:
                for tile in p["tiles"]:
                    x, y, _ = tile["tileXYZ"]
                    im = Image.new("RGB", (source.TILE, source.TILE),
                                   ((x * 17) % 150 + 35, (y * 13) % 150 + 35, 75))
                    target = folder / tile["name"]
                    im.save(target, "JPEG", quality=92)
                    tile["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
                    tile["byteCount"] = target.stat().st_size
            source.render(m, folder)
            self.assertTrue(source.verify(folder))
            self.assertFalse(m["seamDiagnostics"]["gameRoadOrPhotoSeamVerified"])
            self.assertFalse(m["gameArtApproved"])
            changed = copy.deepcopy(m)
            changed["panels"][0]["sourceSha256"] = "0" * 64
            (folder / "manifest.json").write_text(__import__("json").dumps(changed))
            with self.assertRaises(ValueError):
                source.verify(folder)


if __name__ == "__main__":
    unittest.main(verbosity=2)
