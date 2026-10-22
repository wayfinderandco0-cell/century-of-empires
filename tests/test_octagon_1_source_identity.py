"""Prevent source-art drift between V115, V119 and the Octagon 1 editor.

This verifies *image identity*, not road passability, historical accuracy,
bridge connectivity, or production readiness. Source-art review remains required.
"""
import base64
import hashlib
import io
import re
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "v115-town-pan-controls.html",
    "v119-matrei-town-label.html",
    "octagon-1-road-authoring.html",
)
IMAGE_RE = re.compile(r"data:image/jpeg;base64,([A-Za-z0-9+/=]+)")
EXPECTED_SIZE = (1100, 842)


def source_art_sha256(html):
    """Fingerprint exactly one decodable 1100x842 source JPEG in HTML."""
    matches = IMAGE_RE.findall(html)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one embedded source JPEG; found {len(matches)}")
    try:
        raw = base64.b64decode(matches[0], validate=True)
        with Image.open(io.BytesIO(raw)) as image:
            if image.format != "JPEG" or image.size != EXPECTED_SIZE:
                raise ValueError("Unexpected source-art format or dimensions")
            image.verify()
    except (OSError, base64.binascii.Error) as exc:
        raise ValueError("Invalid source JPEG") from exc
    return hashlib.sha256(raw).hexdigest()


def verify_source_art_identity(html_by_name):
    """Fail closed if any reference art differs; never certify the route itself."""
    fingerprints = {name: source_art_sha256(html) for name, html in html_by_name.items()}
    if len(fingerprints) != len(SOURCES) or set(fingerprints) != set(SOURCES):
        raise ValueError("Incomplete Octagon 1 source-art comparison")
    if len(set(fingerprints.values())) != 1:
        raise ValueError("V115, V119 and Octagon 1 editor use different source JPEGs")
    return next(iter(fingerprints.values()))


class OctagonOneSourceIdentityTests(unittest.TestCase):
    def test_three_real_prototypes_share_identical_raw_jpeg(self):
        html = {name: (ROOT / name).read_text(encoding="utf-8") for name in SOURCES}
        digest = verify_source_art_identity(html)
        self.assertEqual(len(digest), 64)

    def test_missing_and_duplicate_image_rejected(self):
        with self.assertRaises(ValueError):
            source_art_sha256("no embedded source")
        with self.assertRaises(ValueError):
            source_art_sha256('data:image/jpeg;base64,AA== data:image/jpeg;base64,AA==')

    def test_corrupt_payload_rejected(self):
        with self.assertRaises(ValueError):
            source_art_sha256('data:image/jpeg;base64,AAAA')

    def test_mismatched_valid_source_art_rejected(self):
        def jpeg_html(rgb):
            buffer = io.BytesIO()
            Image.new("RGB", EXPECTED_SIZE, rgb).save(buffer, format="JPEG")
            return 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode("ascii")
        first = jpeg_html((25, 70, 40))
        second = jpeg_html((30, 70, 40))
        with self.assertRaisesRegex(ValueError, "different source JPEGs"):
            verify_source_art_identity(dict(zip(SOURCES, (first, first, second))))

    def test_incomplete_comparison_rejected(self):
        with self.assertRaises(ValueError):
            verify_source_art_identity({})


if __name__ == "__main__":
    unittest.main()
