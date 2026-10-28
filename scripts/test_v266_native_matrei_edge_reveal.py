#!/usr/bin/env python3
"""Fail-closed V266 alpha-only artifact tests. No production-art approval."""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

script=Path(__file__).with_name('v266_native_matrei_edge_reveal.py')
spec=importlib.util.spec_from_file_location('v266',script)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def fixture():
    return ('const V263_PINS={};const V263_IMAGES={};V263ImportPair;'
            'get productionApproved(){return false};'
            +mod.OLD_TITLE+';'
            +mod.OLD_MASK+';'+mod.OLD_FOCUS+';')

class NativeEdgeReveal(unittest.TestCase):
    def test_exactly_three_textual_changes(self):
        before=fixture();after=mod.transform(before)
        self.assertEqual(after.count(mod.NEW_MASK),1)
        self.assertEqual(after.count(mod.NEW_FOCUS),1)
        self.assertNotIn(mod.OLD_MASK,after)
        self.assertNotIn(mod.OLD_FOCUS,after)
        self.assertIn('get productionApproved(){return false}',after)
        self.assertEqual(after.replace(mod.NEW_MASK,mod.OLD_MASK)
                          .replace(mod.NEW_FOCUS,mod.OLD_FOCUS)
                          .replace(mod.NEW_TITLE,mod.OLD_TITLE),before)
    def test_reflected_seam_or_missing_guard_rejected(self):
        for invalid in (fixture()+'V264_SEAM_UNDERLAY',
                        fixture().replace('get productionApproved(){return false}',''),
                        fixture()+mod.OLD_MASK,
                        fixture().replace('V263ImportPair','')):
            with self.assertRaises(ValueError):mod.transform(invalid)
    def test_wrong_artifact_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'input.html';out=Path(d)/'out.html'
            source.write_text(fixture())
            with self.assertRaises(ValueError):mod.build(source,out)
            self.assertFalse(out.exists())
    def test_real_exact_artifact_when_available(self):
        original=os.getenv('COE_V265_EXACT_HTML')
        if not original:self.skipTest('exact original art HTML is local-only; no CI image approval')
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out.html'
            result=mod.build(original,out)
            self.assertFalse(result['productionApproved'])
            self.assertFalse(result['userVisualApproval'])
            self.assertGreater(out.stat().st_size,10_000_000)

if __name__=='__main__':unittest.main()
