#!/usr/bin/env python3
"""Offline negative controls for nine separate native modern source candidates."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
import v217_matrei_nearby_native_scout as scout

class SourceScoutTests(unittest.TestCase):
    def test_exact_geography_and_no_false_approvals(self):
        m = scout.plan()
        self.assertEqual(len(m["sites"]), 9)
        self.assertEqual(len({tuple(t["xyz"]) for s in m["sites"] for t in s["tiles"]}), 36)
        self.assertTrue(m["geographicGapsBetweenSites"])
        self.assertTrue(all(m[k] is False for k in scout.FLAGS))
        self.assertEqual(m["projection"], "EPSG:3857")
        for s in m["sites"]:
            self.assertEqual(s["nativeOriginXYZ"][2], 18)
            self.assertEqual(len(s["tiles"]), 4)
            self.assertEqual(len(s["footprintLonLat"]), 4)

    def test_reject_invented_registration_and_site_identity(self):
        m = scout.plan()
        m.update(contactFile="x", contactSha256="y")
        for site in m["sites"]:
            site["imageSha256"] = "dummy"
            for tile in site["tiles"]:
                tile.update(sha256="dummy", byteCount=123)
        self.assertTrue(scout.verify_plan(m))
        for change in (
            lambda x: x.update(registeredToV123=True),
            lambda x: x.update(sourcePatchesContiguous=True),
            lambda x: x.update(modernFeaturesExcluded=True),
            lambda x: x.update(periodSafe=True),
            lambda x: x.update(gameArtApproved=True),
            lambda x: x.update(projection="EPSG:4326"),
            lambda x: x["sites"][0].update(nativeOriginXYZ=[0, 0, 18]),
            lambda x: x["sites"][2]["tiles"][0].update(url="https://example.com/fake.jpg"),
        ):
            altered = copy.deepcopy(m)
            change(altered)
            with self.assertRaises(ValueError):
                scout.verify_plan(altered)

    def test_native_pixel_integrity_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            m = scout.plan()
            for i, site in enumerate(m["sites"]):
                for j, tile in enumerate(site["tiles"]):
                    # Unique source-like test JPEGs are SYNTHETIC TEST FIXTURES only.
                    im = Image.new("RGB", (256, 256), ((i * 19 + j * 17) % 255,
                                                       (i * 27 + j * 23) % 255,
                                                       (i * 31 + j * 29) % 255))
                    im.save(folder / tile["name"], "JPEG", quality=91)
                    data = (folder / tile["name"]).read_bytes()
                    tile["sha256"] = hashlib.sha256(data).hexdigest()
                    tile["byteCount"] = len(data)
                scout.assemble(site, folder).save(folder / site["sourceImage"])
            image = scout.contact(m, folder)
            image.save(folder / "matrei-nearby-native-contact.png")
            m["contactFile"] = "matrei-nearby-native-contact.png"
            m["contactSha256"] = scout.sha((folder / m["contactFile"]).read_bytes())
            (folder / "manifest.json").write_text(json.dumps(m))
            self.assertTrue(scout.verify(folder))
            first = folder / m["sites"][0]["tiles"][0]["name"]
            data = first.read_bytes()
            first.write_bytes(data + b"corruption")
            with self.assertRaises(ValueError):
                scout.verify(folder)
            first.write_bytes(data)
            self.assertTrue(scout.verify(folder))
            contact = folder / m["contactFile"]
            with Image.open(contact) as src:
                changed = src.copy()
            changed.putpixel((300, 300), (255, 0, 255))
            changed.save(contact)
            with self.assertRaises(ValueError):
                scout.verify(folder)

if __name__ == "__main__":
    unittest.main(verbosity=2)
