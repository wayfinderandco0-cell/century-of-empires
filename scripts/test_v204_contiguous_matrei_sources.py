#!/usr/bin/env python3
"""Offline fail-closed V204 geographic/source-integrity tests (no network)."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image

import v204_contiguous_matrei_sources as v204


class ContiguousMatreiSourceTests(unittest.TestCase):
    def test_native_geography_is_adjacent_not_game(self):
        m = v204.plan()
        self.assertTrue(v204.validate(m))
        self.assertEqual(len(m["panels"]), 3)
        self.assertEqual(len({tuple(t["tileXYZ"]) for p in m["panels"]
                              for t in p["tiles"]}), 12)
        west, center, south = m["panels"]
        self.assertEqual(west["nativeOriginXYZ"][0] + 2, center["nativeOriginXYZ"][0])
        self.assertEqual(center["nativeOriginXYZ"][1] + 2, south["nativeOriginXYZ"][1])
        self.assertEqual(west["footprintLonLat"][2], center["footprintLonLat"][0])
        self.assertEqual(center["footprintLonLat"][1], south["footprintLonLat"][3])
        for flag in v204.FALSE_FLAGS:
            self.assertIs(m[flag], False)
        self.assertIs(m["sourcePanelsNotRegisteredToV121V123"], True)

    def test_wrong_native_projection_or_game_approval_fails(self):
        m = v204.plan()
        for mutate in (
            lambda x: x.update(projection="EPSG:4326"),
            lambda x: x.update(productionApproved=True),
            lambda x: x["panels"][0].update(nativeOriginXYZ=[0, 0, 18]),
            lambda x: x["panels"][1].update(footprintLonLat=[0, 0, 0, 0]),
            lambda x: x["panels"][2]["tiles"][0].update(url="https://example.invalid/fake.jpeg"),
            lambda x: x.update(historicRoadsVerified=True),
        ):
            changed = copy.deepcopy(m)
            mutate(changed)
            with self.assertRaises(ValueError):
                v204.validate(changed)

    def _fake_tiles(self, m, folder):
        # Generate unique local JPEGs with position-derived pixel values.
        # This exercises source RGB fidelity, never claims source authenticity.
        for p in m["panels"]:
            for t in p["tiles"]:
                x, y, _ = t["tileXYZ"]
                im = Image.new("RGB", (v204.TILE, v204.TILE))
                pixels = im.load()
                for py in range(v204.TILE):
                    for px in range(v204.TILE):
                        pixels[px, py] = ((x * 7 + px // 3) % 180 + 25,
                                          (y * 9 + py // 3) % 170 + 30,
                                          (px // 5 + py // 5) % 120 + 35)
                target = folder / t["name"]
                im.save(target, "JPEG", quality=90)
                t["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
                t["byteCount"] = target.stat().st_size

    def test_exact_source_pixels_and_integrity(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            m = v204.plan()
            self._fake_tiles(m, folder)
            v204.render(m, folder)
            self.assertTrue(v204.verify(folder))
            self.assertFalse(m["seamDiagnostics"]["gameRoadOrPhotoSeamVerified"])
            self.assertEqual(m["contactImage"], "modern-contiguous-reference-contact.png")
            for panel in m["panels"]:
                self.assertLess(panel["nearWhiteFraction"], .60)
            # Tamper the raw JPEG: fail even if decoded pixels might be similar.
            tile = folder / m["panels"][0]["tiles"][0]["name"]
            original = tile.read_bytes()
            tile.write_bytes(original + b"altered")
            with self.assertRaises(ValueError):
                v204.verify(folder)
            tile.write_bytes(original)
            self.assertTrue(v204.verify(folder))
            # Tamper contact pixel without changing source: fail.
            contact = folder / m["contactImage"]
            with Image.open(contact) as im:
                altered = im.copy()
            altered.putpixel((600, 50), (0, 0, 0))
            altered.save(contact)
            with self.assertRaises(ValueError):
                v204.verify(folder)

    def test_source_anchor_and_atlas_frame(self):
        v204.verify_source_invariants()
        center = v204.plan()["panels"][1]["footprintLonLat"]
        lon, lat = v204.ANCHOR
        self.assertTrue(center[0] < lon < center[2])
        self.assertTrue(center[1] < lat < center[3])


if __name__ == "__main__":
    unittest.main(verbosity=2)
