#!/usr/bin/env python3
"""V253 fail-closed source input regressions (no historic or art approval)."""
import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v253qa',ROOT/'scripts/qa_v253_original_art_playtest.py')
qa=importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)

class TestV253OriginalSource(unittest.TestCase):
    def test_distinct_fixture_bytes_and_sha(self):
        r=qa.prepare_sources()
        self.assertNotEqual(r['west']['sha256'],r['south']['sha256'])
        for tile in ('west','south'):
            self.assertEqual(hashlib.sha256(Path(r[tile]['source']).read_bytes()).hexdigest(),r[tile]['sha256'])
            self.assertFalse(r[tile]['humanApproved'])
            self.assertFalse(r[tile]['sourceRegisteredToV123'])
    def test_duplicate_pair_rejected(self):
        same=str(qa.FIXTURES['west'])
        with patch.dict(os.environ,{'WEST_SOURCE':same,'SOUTH_SOURCE':same}):
            with self.assertRaisesRegex(ValueError,'distinct'):
                qa.prepare_sources()
    def test_wrong_native_dimensions_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/'bad.png'
            Image.new('RGB',(512,512),'green').save(bad)
            with patch.dict(os.environ,{'WEST_SOURCE':str(bad)}):
                with self.assertRaisesRegex(ValueError,'1536x1024'):
                    qa.prepare_sources()
    def test_approvals_are_never_inferred_from_sha(self):
        r=qa.prepare_sources()
        self.assertTrue(all(not x[k] for x in r.values() for k in
            ('historical1780RoadVerified','bridgeBanksVerified','humanApproved')))

if __name__=='__main__':unittest.main()
