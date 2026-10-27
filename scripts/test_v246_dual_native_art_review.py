#!/usr/bin/env python3
"""V246 real-pixel synthetic tests; these are NOT finished Alpine art."""
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from PIL import Image, ImageDraw
from v243_road_conditioning import load_routes
from v246_dual_native_art_review import (
    audit_pair, validate_annotation, SYNTHETIC_METHOD
)

ATLAS = Path("terrain-grid/v123-atlas.js")


def fixture(tile, route, extra=False):
    image = Image.new("RGB", (1536, 1024),
                      (33, 90, 50) if tile == "west" else (40, 85, 53))
    d = ImageDraw.Draw(image)
    # Deliberately offset native source road pixels. The V245 warp must move
    # real brown pixels to the unchanged V123 line, not merely redraw it.
    shifted = [[x + (12 if tile == "south" else 0), y + 16] for x, y in route]
    d.line([tuple(p) for p in shifted], fill=(168, 129, 86), width=28,
           joint="curve")
    full = [list(p) for p in shifted]
    start, end = 0, len(full) - 1
    if extra:
        if tile == "west":
            full.insert(0, [0, 550]); start = 1
        else:
            full.append([1450, 610])
    b = io.BytesIO()
    image.save(b, format="PNG")
    raw = b.getvalue()
    manifest = {
        "sourceSha256": hashlib.sha256(raw).hexdigest(),
        "sourceAttribution": "Synthetic geometry regression test ONLY",
        "sourceDescription": "Not an authentic geographic image",
        "annotationMethod": SYNTHETIC_METHOD,
        "fullVisibleRoadPoints": full,
        "playableStartIndex": start,
        "playableEndIndex": end,
    }
    return raw, manifest


class DualArtReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, routes = load_routes(ATLAS)
        cls.routes = {"west": list(reversed(routes["west"])),
                      "south": routes["south"]}

    def test_pair_moves_existing_pixels_without_approval(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            sources, manifests = {}, {}
            for tile in ("west", "south"):
                raw, manifest = fixture(tile, self.routes[tile])
                sources[tile] = td / (tile + ".png")
                sources[tile].write_bytes(raw)
                manifests[tile] = manifest
            out = td / "out"
            report = audit_pair(ATLAS, sources, manifests, out,
                                allow_synthetic=True)
            self.assertTrue(report["bothNecessaryGeometryPassed"], report)
            self.assertFalse(report["candidateMayEnterSeparateBrowserReview"])
            self.assertFalse(report["productionApproved"])
            for tile in ("west", "south"):
                self.assertTrue((out / f"{tile}-native-warp-UNAPPROVED.png").is_file())
                self.assertTrue(report["tiles"][tile]["warpedRoadEvidence"]["visibleEarthPass"])
                self.assertGreater(report["tiles"][tile]["warp"]["maximumDisplacementPx"], 10)
            evidence = os.getenv("V246_SYNTHETIC_OUT")
            if evidence:
                target = Path(evidence); target.mkdir(parents=True, exist_ok=True)
                for name in ("west-v123-overlay-UNAPPROVED.jpg",
                             "south-v123-overlay-UNAPPROVED.jpg", "report.json"):
                    (target / name).write_bytes((out / name).read_bytes())

    def test_reject_west_and_south_unverified_visible_continuations(self):
        for tile in ("west", "south"):
            raw, manifest = fixture(tile, self.routes[tile], extra=True)
            with self.assertRaisesRegex(ValueError, "beyond immutable survey limit"):
                validate_annotation(manifest, raw, allow_synthetic=True)

    def test_reject_hash_tamper_and_unverified_annotator(self):
        raw, manifest = fixture("west", self.routes["west"])
        manifest["sourceSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA256"):
            validate_annotation(manifest, raw, allow_synthetic=True)
        manifest["sourceSha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, "independently traced"):
            validate_annotation(manifest, raw)

    def test_reject_missing_full_road_trace(self):
        raw, manifest = fixture("south", self.routes["south"])
        del manifest["playableEndIndex"]
        with self.assertRaisesRegex(ValueError, "survey indices"):
            validate_annotation(manifest, raw, allow_synthetic=True)

    def test_reject_duplicate_source_images(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "same.png"
            raw, manifest = fixture("west", self.routes["west"])
            p.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "identical source"):
                audit_pair(ATLAS, {"west": p, "south": p},
                           {"west": manifest, "south": manifest}, Path(td) / "out",
                           allow_synthetic=True)


if __name__ == "__main__":
    unittest.main()
