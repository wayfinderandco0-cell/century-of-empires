#!/usr/bin/env python3
"""V218 fail-closed tests: source pixels unchanged, excluded pixels unavailable."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
import v218_reviewed_modern_quarantine as q

class ModernQuarantineTests(unittest.TestCase):
    def make_fixture(self, folder):
        manifest = q.plan()
        for site in manifest["sites"]:
            ref = q.scout.plan()["sites"][site["siteIndex"]]
            for i, (got, tile) in enumerate(zip(site["sourceTiles"], ref["tiles"])):
                # Clearly synthetic test JPEGs; never used as actual Alpine material.
                im = Image.new("RGB", (256, 256),
                               ((site["siteIndex"] * 17 + i * 23) % 255,
                                (site["siteIndex"] * 29 + i * 19) % 255,
                                (site["siteIndex"] * 11 + i * 31) % 255))
                im.save(folder / tile["name"], "JPEG", quality=93)
                data = (folder / tile["name"]).read_bytes()
                got["sha256"], got["byteCount"] = q.sha(data), len(data)
            rgb = q.source_site(site, folder)
            mask = q.mask_for(site)
            art = q.quarantined(rgb, mask)
            for key, im, digest in (
                ("originalFile", rgb, "sourceSha256"),
                ("maskFile", mask, "maskSha256"),
                ("quarantineFile", art, "quarantineSha256"),
            ):
                im.save(folder / site[key])
                site[digest] = q.sha((folder / site[key]).read_bytes())
            site["sourcePixelsSha256"] = q.sha(rgb.tobytes())
            site["retainedPixels"] = sum(1 for v in mask.getdata() if v)
            site["excludedPixels"] = q.SIZE ** 2 - site["retainedPixels"]
        manifest["contactFile"] = "v218-original-versus-quarantine.png"
        q.contact(manifest["sites"], folder).save(folder / manifest["contactFile"])
        manifest["contactSha256"] = q.sha((folder / manifest["contactFile"]).read_bytes())
        (folder / "manifest.json").write_text(json.dumps(manifest))
        return manifest

    def test_geometry_and_no_false_approval(self):
        m = q.plan()
        self.assertEqual(m["siteIndices"], [3, 5, 6, 8])
        self.assertEqual(len(m["sites"]), 4)
        self.assertTrue(m["sourceGapsRemainUnknown"])
        self.assertTrue(m["remainingModernFeaturesMayExist"])
        self.assertEqual(m["projection"], "EPSG:3857")
        self.assertTrue(all(m[key] is False for key in q.FLAGS))
        for site in m["sites"]:
            self.assertEqual(len(site["sourceTiles"]), 4)
            self.assertEqual(site["originXYZ"][2], 18)

    def test_reviewed_masks_exclude_dates_and_features_but_keep_natural_pixels(self):
        known = {
            3: ((316, 159), (408, 345), (150, 300)),
            5: ((62, 159), (220, 130), (390, 290)),
            6: ((318, 31), (120, 215), (430, 420)),
            8: ((383, 351), (480, 350), (200, 220)),
        }
        for site in q.plan()["sites"]:
            date, modern, natural = known[site["siteIndex"]]
            mask = q.mask_for(site)
            self.assertEqual(mask.getpixel(date), 0, site["siteId"])
            self.assertEqual(mask.getpixel(modern), 0, site["siteId"])
            self.assertEqual(mask.getpixel(natural), 255, site["siteId"])
            # Secondary modern artifacts spotted in the first REAL CI contact.
            secondary = {3: (470, 341), 5: (62, 278),
                         6: (425, 207), 8: (12, 12)}
            self.assertEqual(mask.getpixel(secondary[site["siteIndex"]]), 0,
                             site["siteId"] + " secondary track/structure")
            original = Image.new("RGB", (512, 512), (47, 121, 73))
            quarantined = q.quarantined(original, mask)
            self.assertEqual(quarantined.getpixel(date), (0, 0, 0, 0))
            self.assertEqual(quarantined.getpixel(natural), (47, 121, 73, 255))
            self.assertGreater(sum(1 for v in mask.getdata() if v), 50000)

    def test_full_synthetic_fixture_integrity_and_tamper_controls(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            manifest = self.make_fixture(folder)
            self.assertTrue(q.verify(folder))
            altered = copy.deepcopy(manifest)
            for change in (
                lambda x: x.update(periodSafe=True),
                lambda x: x.update(allModernFeaturesExcluded=True),
                lambda x: x.update(registeredToV123=True),
                lambda x: x.update(sourceGapsRemainUnknown=False),
                lambda x: x["sites"][0]["reviewedMasks"]["dates"][0].__setitem__(0, 10),
                lambda x: x["sites"][1]["sourceTiles"][0]["xyz"].__setitem__(0, 1),
                lambda x: x["sites"][2].update(excludedPixels=0),
            ):
                modified = copy.deepcopy(altered)
                change(modified)
                (folder / "manifest.json").write_text(json.dumps(modified))
                with self.assertRaises(ValueError):
                    q.verify(folder)
            (folder / "manifest.json").write_text(json.dumps(manifest))
            self.assertTrue(q.verify(folder))

            for key in ("maskFile", "quarantineFile", "originalFile"):
                p = folder / manifest["sites"][0][key]
                original_bytes = p.read_bytes()
                with Image.open(p) as im:
                    changed = im.copy()
                changed.putpixel((150, 300), 0 if key == "maskFile" else
                                 ((255, 0, 255, 255) if key == "quarantineFile"
                                  else (255, 0, 255)))
                changed.save(p)
                with self.assertRaises(ValueError):
                    q.verify(folder)
                p.write_bytes(original_bytes)
            source = folder / manifest["sites"][0]["sourceTiles"][0]["name"]
            old = source.read_bytes()
            source.write_bytes(old + b"tampered")
            with self.assertRaises(ValueError):
                q.verify(folder)
            source.write_bytes(old)
            self.assertTrue(q.verify(folder))

if __name__ == "__main__":
    unittest.main(verbosity=2)
