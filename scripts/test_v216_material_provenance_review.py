#!/usr/bin/env python3
"""V216 negative controls: provenance and native-pixel study never assert game art."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image

import v216_material_provenance_review as study

class NativeSourceStudyTests(unittest.TestCase):
    def test_crop_never_upscales_or_distorts(self):
        a = Image.new("RGB", (512, 512), (23, 51, 76))
        patch, rect = study.native_crop(a)
        self.assertEqual(rect, [0, 0, 512, 512])
        self.assertEqual(patch.tobytes(), a.tobytes())
        with self.assertRaises(ValueError):
            study.native_crop(Image.new("RGB", (511, 512)))
        with self.assertRaises(ValueError):
            study.native_crop(a, (0, 0, 511, 512))
        with self.assertRaises(ValueError):
            study.native_crop(a, (-1, 0, 511, 512))

    def fixture(self, root, atlas):
        for name in ("terrain-v94", "terrain-v97", "terrain-v102"):
            (root / name).mkdir(parents=True)
        atlas.mkdir()
        (root / "terrain-v94/manifest.json").write_text(json.dumps({
            "projection": "equirectangular", "atlasSize": [8192, 6144]}))
        (root / "terrain-v97/manifest.json").write_text(json.dumps({
            "elevationSource": "Copernicus DEM GLO-30 Public 2021",
            "imageSize": [1552, 1782], "boundsLonLat": [11.26, 46.8, 11.8, 47.42]}))
        (root / "terrain-v102/manifest.json").write_text(json.dumps({
            "broadBoundsLonLat": [11.26, 46.8, 11.8, 47.42],
            "sources": {"art": "Original deterministic material and tree crowns",
                        "path": "Illustrative pack trail, NOT surveyed"}}))
        Image.new("RGB", (1448, 1086), (66, 71, 88)).save(root / "terrain-v94/overview.webp")
        Image.new("RGB", (1552, 1782), (88, 83, 76)).save(root / "terrain-v97/brenner-relief.webp")
        Image.new("RGB", (2048, 2048), (62, 95, 53)).save(root / "terrain-v102/navis-material.webp")
        modern = Image.new("RGBA", (1024, 1024), (75, 99, 67, 255))
        for x, y in ((4, 4), (520, 4), (520, 520)):
            modern.putpixel((x, y), (0, 0, 0, 0))
        modern.save(atlas / "native.png")
        report = {"projection": "EPSG:3857", "sourceImagePixels": [1024, 1024],
                  "sourcePanelsGeographicallyContiguous": True,
                  "allRetainedPixelsBitIdenticalToDecodedSource": True,
                  "sourceAtlasFile": "native.png", "sourceAtlasSha256": study.sha(atlas / "native.png")}
        report.update({k: False for k in study.native.FALSE_FLAGS})
        (atlas / "manifest.json").write_text(json.dumps(report))

    def test_classifies_procedural_material_as_not_photographic(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "root"
            atlas = root / "qa/v216-native-atlas"
            root.mkdir()
            atlas.parent.mkdir()
            self.fixture(root, atlas)
            sheet, rows = study.draw_contact(root, atlas)
            self.assertEqual(sheet.width, 1536)
            self.assertEqual(len(rows), 6)
            self.assertFalse(any(row["verified1780Landscape"] or row["registeredToV123"] for row in rows))
            self.assertEqual([row["nativePhotographicModernSource"] for row in rows],
                             [False, False, False, True, True, True])
            self.assertTrue(all(row["cropNeverResampled"] for row in rows))
            self.assertTrue(all(row["transparentQuarantinedPixelsInCrop"] > 0 for row in rows[3:]))
            # A false claim that V102 was real photography must fail closed.
            path = root / "terrain-v102/manifest.json"
            obj = json.loads(path.read_text())
            obj["sources"]["art"] = "Aerial photograph"
            path.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                study.draw_contact(root, atlas)

    def test_source_approval_tamper_and_missing_masks_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "root"
            atlas = root / "qa/v216-native-atlas"
            root.mkdir()
            atlas.parent.mkdir()
            self.fixture(root, atlas)
            path = atlas / "manifest.json"
            obj = json.loads(path.read_text())
            obj["gameArtApproved"] = True
            path.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                study.draw_contact(root, atlas)
            obj["gameArtApproved"] = False
            path.write_text(json.dumps(obj))
            Image.new("RGBA", (1024, 1024), (20, 40, 60, 255)).save(atlas / "native.png")
            with self.assertRaises(ValueError):
                study.draw_contact(root, atlas)

if __name__ == "__main__":
    unittest.main(verbosity=2)
