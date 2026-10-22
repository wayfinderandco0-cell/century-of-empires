#!/usr/bin/env python3
"""Verify Octagon 1 road diagnostics use the exact reviewed source art."""
import hashlib
import io
import sys
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from qa_octagon_1_raw_road import verify_source_blob, SOURCE_BLOB_SHA


class SourcePinTests(unittest.TestCase):
    def test_checked_in_jpeg_matches_pinned_git_blob(self):
        raw = (ROOT / "terrain-grid/octagon-1-v119-source.jpg").read_bytes()
        self.assertEqual(verify_source_blob(raw), SOURCE_BLOB_SHA)
        editor = (ROOT / "octagon-1-road-authoring.html").read_text(encoding="utf-8")
        self.assertIn('sourceBlobSha:"' + SOURCE_BLOB_SHA + '"', editor)

    def test_modified_jpeg_of_same_dimensions_is_rejected(self):
        def jpeg(rgb):
            buf = io.BytesIO()
            Image.new("RGB", (1100, 842), rgb).save(buf, format="JPEG")
            return buf.getvalue()
        original = jpeg((70, 100, 40))
        changed = jpeg((90, 100, 40))
        digest = hashlib.sha1(b"blob " + str(len(original)).encode() + b"\0" + original).hexdigest()
        self.assertEqual(verify_source_blob(original, digest), digest)
        with self.assertRaisesRegex(ValueError, "Source JPEG changed"):
            verify_source_blob(changed, digest)

    def test_non_byte_source_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_source_blob("not image bytes")


if __name__ == "__main__":
    unittest.main()
