#!/usr/bin/env python3
"""V263 synthetic CI tests. Exact V258/V260 PNGs are NOT hosted in GitHub."""
import hashlib, importlib.util, subprocess, tempfile, unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v263',ROOT/'scripts/v263_offline_exact_art_playable.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class V263Tests(unittest.TestCase):
 def test_protected_road_graph(self):
  self.assertEqual(subprocess.check_output(['git','hash-object','terrain-grid/v123-atlas.js'],cwd=ROOT,text=True).strip(),
                   '09f04b4062e24fbacbb645307462cdddce2b2aa3')
  self.assertEqual(subprocess.check_output(['git','hash-object','v121-octagon-1-painted-road.html'],cwd=ROOT,text=True).strip(),
                   '4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382')

 def test_synthetic_build_and_fail_closed_hashes(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);west=p/'west.png';south=p/'south.png'
   Image.new('RGB',(1536,1024),(52,83,64)).save(west)
   Image.new('RGB',(1536,1024),(101,82,57)).save(south)
   original=mod.PINS
   try:
    mod.PINS={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in [('west',west),('south',south)]}
    out=p/'unapproved.html'
    report=mod.build(ROOT,west,south,out)
    data=out.read_text()
    self.assertIn('async function V263ImportPair()',data)
    self.assertIn('get v263ExactArtLoaded()',data)
    self.assertIn('if(imported&&!rawArtReview)',data)
    self.assertIn('get productionApproved(){return false}',data)
    self.assertNotIn('<script src=',data)
    self.assertIn('V263 ORIGINAL ART REJECTED',data)
    self.assertIn('V263_MATREI_HTML=',data)
    self.assertIn('V263_MANIFEST=',data)
    self.assertFalse(report['productionApproved'])
    self.assertFalse(report['webkitTested'])
    with self.assertRaises(AssertionError):mod.build(ROOT,south,west,p/'swapped.html')
   finally:mod.PINS=original

 def test_sha_fallback_not_a_hash_bypass(self):
  js=(ROOT/'scripts/v263_sha256_fallback.js').read_text()
  self.assertIn("if(!window.crypto?.subtle)",js)
  self.assertIn("algo!=='SHA-256'",js)
  self.assertIn('return sha256(bytes)',js)
  self.assertNotIn('expectedSha256:undefined',js)

if __name__=='__main__':unittest.main()
