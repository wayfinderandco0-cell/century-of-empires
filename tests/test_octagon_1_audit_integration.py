"""Integration checks against the actual embedded Octagon 1 source JPEG.

These checks validate evidence extraction and fail-closed reporting only.
They do NOT establish a painted cartway, historical road, or usable crossing.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts import audit_octagon_1_edge as edge
from scripts import audit_octagon_1_source_art as art
from tests.test_octagon_1_source_identity import SOURCES, verify_source_art_identity

ROOT = Path(__file__).resolve().parents[1]


class RawSourceIntegrationTests(unittest.TestCase):
    def test_real_jpeg_and_both_audits_agree_without_approving_route(self):
        html_by_name = {
            name: (ROOT / name).read_text(encoding="utf-8") for name in SOURCES
        }
        digest = verify_source_art_identity(html_by_name)
        source_image, raw_jpeg, route = art.extract(
            html_by_name["octagon-1-road-authoring.html"]
        )
        self.assertEqual(digest, hashlib.sha256(raw_jpeg).hexdigest())
        self.assertEqual(source_image.size, (1100, 842))
        self.assertEqual(route[0], [699, 799])
        self.assertEqual(route[-1], [1100, 704])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            art_dir, edge_dir = root / "source", root / "edge"
            art_result = art.run(html_by_name["octagon-1-road-authoring.html"], art_dir)
            edge_result = edge.run(html_by_name["octagon-1-road-authoring.html"], edge_dir)

            self.assertEqual(art_result["source_jpeg_sha256"], digest)
            self.assertEqual(art_result["status"], "REVIEW_REQUIRED")
            self.assertEqual(len(art_result["raw_source_samples"]), 16)
            self.assertEqual(len(edge_result["frames"]), 6)
            self.assertEqual(edge_result["source_jpeg_bytes"], len(raw_jpeg))
            self.assertEqual(edge_result["candidate_endpoint"], [1100, 704])
            self.assertFalse(edge_result["endpoint_is_source_pixel"])
            self.assertTrue(edge_result["endpoint_on_east_image_boundary"])

            for result in (art_result, edge_result):
                self.assertFalse(result["road_surface_verified"])
                self.assertFalse(result["neighbor_art_verified"])
                self.assertFalse(result["production_ready"])
            for key in ("historical_road_verified", "far_bank_verified"):
                self.assertFalse(art_result[key])
            self.assertFalse(edge_result["bridge_continuation_verified"])

            with Image.open(art_dir / "raw-jpeg-road-contact-sheet.png") as sheet:
                self.assertEqual(sheet.size, (560, 704))
            self.assertEqual(
                json.loads((art_dir / "audit.json").read_text())["source_jpeg_sha256"],
                digest,
            )
            self.assertEqual(
                json.loads((edge_dir / "edge-audit.json").read_text())["review_status"],
                "NEIGHBOR_ART_AND_PAINTED_ROAD_UNVERIFIED",
            )

            for frame in edge_result["frames"]:
                crop_path = edge_dir / frame["filename"]
                self.assertTrue(crop_path.is_file())
                with Image.open(crop_path) as crop:
                    self.assertEqual(crop.size, (128, 128))
                    # Check that a known source pixel is copied without an
                    # overlay, not just that an image file was generated.
                    left, top, right, bottom = frame["source_bounds"]
                    if left < right and top < bottom:
                        x, y = left, top
                        dst_x = x - (frame["point"][0] - 64)
                        dst_y = y - (frame["point"][1] - 64)
                        self.assertEqual(
                            crop.getpixel((dst_x, dst_y)),
                            source_image.getpixel((x, y)),
                        )

    def test_edge_point_is_outside_source_pixels(self):
        status = edge.boundary_status((1100, 842), (1100, 704))
        self.assertFalse(status["endpoint_is_source_pixel"])
        self.assertFalse(status["neighbor_art_verified"])
        self.assertFalse(status["production_ready"])


if __name__ == "__main__":
    unittest.main()
