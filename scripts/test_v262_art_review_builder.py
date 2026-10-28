#!/usr/bin/env python3
"""V262 viewer checks. Exact-source test SKIPS when local PNGs are unavailable."""
import importlib.util, os, tempfile, unittest
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v262',ROOT/'v262_art_review_builder.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
WEST=Path(os.environ.get('V262_WEST','/nonexistent/v262-west.png'))
SOUTH=Path(os.environ.get('V262_SOUTH','/nonexistent/v262-south.png'))

class V262Tests(unittest.TestCase):
 def test_immutable_v123_geometry(self):
  self.assertEqual(module.ROADS['west'][0],[1536,478]);self.assertEqual(module.ROADS['west'][-1],[275,550])
  self.assertEqual(module.ROADS['south'][0],[466,0]);self.assertEqual(module.ROADS['south'][-1],[1270,605])
  self.assertIn('productionApproved',module.build.__code__.co_consts.__repr__())
 def test_reject_mismatched_art(self):
  with tempfile.TemporaryDirectory() as d:
   wrong=Path(d)/'wrong.png';Image.new('RGB',(1536,1024)).save(wrong)
   with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):
    module.check(wrong,'west')
 def test_reject_swapped_pair(self):
  if not WEST.is_file() or not SOUTH.is_file():self.skipTest('Exact original PNGs not hosted in CI')
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):module.build(SOUTH,WEST,Path(d)/'viewer.html')
 def test_exact_source_embedded(self):
  if not WEST.is_file() or not SOUTH.is_file():self.skipTest('Exact original PNGs not hosted in CI')
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'viewer.html';r=module.build(WEST,SOUTH,target)
   s=target.read_text();self.assertTrue(s.startswith('<!doctype html>'))
   self.assertEqual(s.count('data:image/png;base64,'),2)
   self.assertIn('[[1536,478],[1450,478]',s)
   self.assertIn('[[466,0],[466,74]',s)
   self.assertFalse(r['productionApproved']);self.assertFalse(r['actualGameplayRenderer'])

if __name__=='__main__':unittest.main()
