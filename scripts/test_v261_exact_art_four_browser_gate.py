#!/usr/bin/env python3
"""V261: synthetic QA regressions never imply artwork approval."""
import hashlib, tempfile, unittest
from pathlib import Path
import numpy as np
from PIL import Image
from v261_exact_art_four_browser_gate import verify_sources,assess_captures

class TestV261(unittest.TestCase):
 def test_missing_source_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(FileNotFoundError):verify_sources(Path(d)/'west',Path(d)/'south')
 def test_bad_source_hash_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d);Image.new('RGB',(1536,1024),'green').save(a/'west.png')
   Image.new('RGB',(1536,1024),'blue').save(a/'south.png')
   with self.assertRaises(ValueError):verify_sources(a/'west.png',a/'south.png')
 def test_exact_hash_pair(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d);Image.new('RGB',(1536,1024),'green').save(a/'west.png')
   Image.new('RGB',(1536,1024),'blue').save(a/'south.png')
   expected={t:hashlib.sha256((a/(t+'.png')).read_bytes()).hexdigest() for t in ('west','south')}
   self.assertEqual(verify_sources(a/'west.png',a/'south.png',expected),expected)
 def test_missing_capture_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d);r=assess_captures(a/'empty',a/'out')
   self.assertFalse(r['strictV203Passed']);self.assertEqual(len(r['missingRawScreenshots']),12)
 def test_synthetic_pass_still_never_approves(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d);(a/'raw').mkdir()
   pixels=np.random.default_rng(261).integers(0,256,(400,400,3),dtype=np.uint8)
   for e in ('chromium','webkit'):
    for o in ('portrait','landscape'):
     for t in ('west','matrei','south'):
      Image.fromarray(pixels).save(a/'raw'/f'{e}-{o}-{t}-RAW-UNAPPROVED.png')
   r=assess_captures(a/'raw',a/'out')
   self.assertTrue(r['strictV203Passed']);self.assertFalse(r['productionApproved'])
   self.assertFalse(r['humanVisualApproval']);self.assertFalse(r['bridgeBanksVerified'])
   src=(a/'raw/webkit-portrait-west-RAW-UNAPPROVED.png').read_bytes()
   dst=(a/'out/v203-input/webkit-portrait-west-close.png').read_bytes()
   self.assertEqual(src,dst)
 def test_local_partial_actual_captures(self):
  import os
  path=os.environ.get('V259_CAPTURE_DIR')
  if not path:self.skipTest('Local V259 screenshots unavailable in CI')
  with tempfile.TemporaryDirectory() as d:
   r=assess_captures(Path(path),Path(d))
   self.assertFalse(r['strictV203Passed']);self.assertGreater(len(r['missingRawScreenshots']),0)
if __name__=='__main__':unittest.main()
